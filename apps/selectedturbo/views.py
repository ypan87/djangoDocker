import json
import xlsxwriter
import io
from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.db import transaction
from .services.project import Project
from .services.design_points import RatedPoint, DutyPoint
from .services.base_points import BasePoint, UploadPoint
from .services.turbo_data import TurboData
from .services.turbo_calculation import *
from .forms import SelectionForm
from .forms import ProjectForm
from .models import Turbo, TestPoints, Sizer
from .models import Project as TurboProject
from users.models import UserProfile
from .services.const import LANGUAGE,TRANSLATION

def initial_turbo_list():
    type_list = ["GL1", "GL2", "GL3", "GL5", "GL8", "GL10", "GL15", "GL20", "GL30", "GL50"]
    turbo_list = []

    for type in type_list:
        turbos = Turbo.objects.filter(category=type).order_by("cut_back")[:4]
        # TODO 判断种类以及数量
        for turbo in turbos:
            turbo_data = TurboData(turbo)
            turbo_list.append(turbo_data)

    return turbo_list

def get_all_base_points(turbo_calculation, upload_data, category="GL3"):
    base_points_collection = []
    if not upload_data:
        for x in range(1, 12):
            condition_collection = []
            for y in range (1, 9):
                point_set = TestPoints.objects.filter(working_condition=x, working_position=y)[:1]
                point = point_set[0]
                base_point = BasePoint(point)
                condition_collection.append(base_point)
            base_points_collection.append(condition_collection)

    else:
        base_points_collection = get_base_points_from_upload_data(upload_data)

    turbo_calculation.add_base_point_list(base_points_collection)

def initiate_rated_point(post_data, project, turbo_calculation):
    rp_inlet_temp = float(post_data.get("ratingPointInletTemp", 0))
    rp_inlet_humi = float(post_data.get("ratingPointHumi", 0))
    rp_outlet_press = float(post_data.get("ratingPointOutPressure", 0))
    rp_inlet_press = float(post_data.get("ratingPointInletPressure", 0))
    rp_inlet_press_loss = float(post_data.get("ratingPointInletLoss", 0))
    rp_outlet_press_loss = float(post_data.get("ratingPointOutletLoss", 0))
    is_imperial = get_is_imperial(post_data)
    point = RatedPoint(rp_inlet_temp, rp_inlet_humi, rp_outlet_press, 1,
                       project, is_imperial, False, rp_inlet_press, rp_inlet_press_loss,
                       rp_outlet_press_loss)
    turbo_calculation.add_rated_point(point)

def get_is_imperial(post_data):
    if post_data.get("isImperial") == "metric":
        return False
    else:
        return True

# 初始化project TODO 项目初始化有需要更新
def initiate_project(post_data):
    turbo_list = initial_turbo_list()
    pj_altitude = float(post_data.get("projectAltitude", ""))
    pj_inlet_press = float(post_data.get("projectInletPres", ""))
    pj_frequency = int(post_data.get("frequencySelect", ""))
    pj_machine_num = int(post_data.get("projectUnitsNum", ""))
    pj_volt = int(post_data.get("projectVolt", ""))
    pj_security_coeff = float(post_data.get("projectSafetyFactor", ""))
    pj_ei_rating = int(post_data.get("projectEIRating", ""))
    pj_amb_temp = float(post_data.get("projectEnvTemp", ""))
    pj_standard_flow = float(post_data.get("ratingFlow", 0))
    pj_standard_press = float(post_data.get("ratingPressure", 0))
    pj_standard_temp = float(post_data.get("ratingTemp", 0))
    pj_standard_humi = float(post_data.get("ratingHumi", 0))
    pj_is_imperial = get_is_imperial(post_data)
    pj_max_flow_coeff = float(post_data.get("maxFlowCoeff", 0))
    pj_pressure_coeff = float(post_data.get("maxPressureCoeff", 0))

    return Project(pj_max_flow_coeff, pj_pressure_coeff, turbo_list, pj_altitude, pj_is_imperial, False,
                   pj_inlet_press, pj_frequency, pj_machine_num, pj_volt, "ALU", pj_security_coeff,
                   pj_ei_rating, pj_amb_temp, pj_standard_flow, pj_standard_press,
                   pj_standard_temp, pj_standard_humi)

# 获取工况曲线所有工况点的集合
def get_single_condition_collection(condition, post_data):
    inlet_pressure = float(condition.get("pressure"))
    temp = float(condition.get('temp'))
    humi = float(condition.get('humi'))
    is_imperial = get_is_imperial(post_data)

    duty_point_collection = []
    for point in condition.get("points"):
        flow = float(point.get("flow")) / 100
        pressure = float(point.get("pressure"))
        duty_point = DutyPoint(temp, humi, pressure, flow, False, is_imperial, inlet_pressure)
        duty_point_collection.append(duty_point)
    return duty_point_collection

# 获取普通工况点集合
def get_normal_points(post_data, turbo_calculation):
    condition_array = post_data.get('workingConditions', [])
    condition_collection = []
    for condition in condition_array:
        duty_points_collection = get_single_condition_collection(condition, post_data)
        condition_collection.append(duty_points_collection)
    turbo_calculation.add_duty_point_list(condition_collection)

def add_chart_to_excel(conditions, worksheet, worksheet2, workbook, lang):
    graph_column_index = 6
    graph_row_index = 0
    test_point_row_start_index = 0
    test_point_column_start_index = 0
    flow_pressure_row_start_index = 0
    flow_pressure_column_start_index = 3
    flow_power_row_start_index = 0
    flow_power_column_start_index = 6

    for condition in conditions:
        # chart需要首先在表格中加入数据
        chart = workbook.add_chart({'type': 'scatter', 'subtype': 'smooth'})
        base_data_set = condition[0]
        for curve in base_data_set:
            test_point_row_start_index = add_chart_series(
                chart,
                curve,
                test_point_row_start_index,
                test_point_column_start_index,
                worksheet2,
                {
                    "smooth": True
                }
            )


        flow_pressure_data_set = condition[2]
        flow_pressure_row_start_index = add_chart_series(
            chart,
            flow_pressure_data_set,
            flow_pressure_row_start_index,
            flow_pressure_column_start_index,
            worksheet2,
            {
                "marker": {
                    'type': 'triangle',
                    'size': 8
                },
                "line": {
                    "none": True
                }
            }
        )

        power_data_set = condition[1]
        flow_power_row_start_index = add_chart_series(
            chart,
            power_data_set,
            flow_power_row_start_index,
            flow_power_column_start_index,
            worksheet2,
            {
                "marker": {
                    'type': 'circle',
                    'size': 8
                },
                'y2_axis': True,
                "smooth": False,
                'line': {'dash_type': 'dash'},
            }
        )
        # 插入图表
        chart.set_legend({'none': True})
        worksheet.insert_chart(graph_row_index, graph_column_index, chart, {'x_offset': 10, 'y_offset': 10})
        graph_row_index += 20

def add_chart_series(chart, curve_data_set, row_index, column_index, worksheet2, more_options):
    curve_length = len(curve_data_set)
    point_position = {"start_row": row_index, "end_row": row_index + curve_length - 1}
    for num, value in enumerate(curve_data_set):
        worksheet2.write(row_index + num, column_index, value[0])
        worksheet2.write(row_index + num, column_index + 1, value[1])
    opts = {
        'categories': [
            'Sheet2',
            point_position.get('start_row'),
            column_index,
            point_position.get("end_row"),
            column_index
        ],
        'values': [
            'Sheet2',
            point_position.get("start_row"),
            column_index + 1,
            point_position.get("end_row"),
            column_index + 1
        ],
    }
    chart.add_series({
        **opts, **more_options
    })

    return row_index + curve_length + 2

def add_table_to_excel(worksheet, workbook, table_data, lang):
    start_row_index = 0
    start_column_index = 0
    table_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
    })

    for condition in table_data.get('conditions'):
        dataset = condition.get("dataSet")
        new_dataset = []
        for point in dataset:
            point_data = []
            point_data.append(point.get("relativeFlow"))
            point_data.append(point.get("outletPress"))
            point_data.append(point.get("flowAmb"))
            point_data.append(point.get("shaftPower"))
            point_data.append(point.get("wirePower"))
            new_dataset.append(point_data)

        data = [
                   [
                       TRANSLATION[lang]["blower_category"] + "：%s" % table_data.get("turbo"),
                       "%sC/%s%%" % (condition.get("temp"), condition.get("humidity")),
                   ],
                   [
                       TRANSLATION[lang]["inlet_pressure"],
                       "%s bara" % condition.get("baraPressure"),
                   ],
                   [
                       TRANSLATION[lang]["relative_flow"],
                       "ΔP",
                       TRANSLATION[lang]["flow"],
                       TRANSLATION[lang]["shaftPower"],
                       TRANSLATION[lang]["wirePower"],
                   ],
                   ["%", "barG", "m3/h", "kW", "kW"],
               ] + new_dataset

        for row_num, columns in enumerate(data):
            worksheet.write_row(start_row_index + row_num, start_column_index, columns, table_format)

        worksheet.merge_range(
            start_row_index,
            start_column_index + 1,
            start_row_index,
            start_column_index + 4,
            data[0][1],
            table_format
        )
        worksheet.merge_range(
            start_row_index + 1,
            start_column_index + 1,
            start_row_index + 1,
            start_column_index + 4,
            data[1][1],
            table_format
        )

        start_row_index += len(data) + 2

    # 设置单元格大小
    worksheet.set_column(0, 0, 30)
    for n in range(start_column_index + 1, start_column_index + 10):
        worksheet.set_column(n, n, 15)

    return start_row_index

def get_lang_url(alias_name, kwargs):
    lang_urls = {
        LANGUAGE["en"]: reverse(alias_name, kwargs={**{"lang": LANGUAGE["en"]}, **kwargs}),
        LANGUAGE["cn"]: reverse(alias_name, kwargs={**{"lang": LANGUAGE["cn"]}, **kwargs})
    }
    return lang_urls

def file_validation(file):
    if not file:
        return True, ""
    if not file.name.endswith(".csv"):
        return False, ""
    if file.size > 1024*10:
        return False, ""
    file_data = file.read().decode("utf-8")
    lines = file_data.split("\n")
    if len(lines) != 8:
        return False, ""
    upload_dataset = []
    for line in lines:
        dataset = line.split(",")
        if len(dataset) != 33:
            return False, ""
        for i, data in enumerate(dataset):
            dataset[i] = dataset[i].rstrip("%\r")
            try:
                dataset[i] = float(dataset[i])
            except Exception as e:
                return False, ""
        upload_dataset.append(dataset)

    return True, upload_dataset

def get_base_points_from_upload_data(upload_data):

    base_points_collection = []
    for x in range(0, 11):
        condition_collection = []
        for y in range(0, 8):
            flow_coef = upload_data[y][x*3]
            pressure_coef = upload_data[y][x*3 + 1]
            efficiency = upload_data[y][x*3 + 2] / 100
            uploadPoint = UploadPoint(flow_coef, pressure_coef, efficiency)
            base_point = BasePoint(uploadPoint)
            condition_collection.append(base_point)
        base_points_collection.append(condition_collection)
    return base_points_collection

class CheckBlowerView(LoginRequiredMixin, View):
    def post(self, request, lang="cn"):

        if lang not in LANGUAGE:
            return HttpResponse(
                json.dumps(
                    {
                        "status": "failure",
                        "errorCode": "URLNotExist",
                        "lang": lang
                    }
                ),
                content_type="application/json"
            )

        # 数据验证
        form = SelectionForm(request.POST)

        if not form.is_valid():
            return HttpResponse(
                json.dumps({
                    "status": "failure",
                    "errorCode": "ParameterError",
                    "lang": lang,
                }),
                content_type="application/json"
            )
        upload_data = ""
        if "uploadFile" in request.FILES:
            upload_file = request.FILES["uploadFile"]
            is_valid, upload_data = file_validation(upload_file)
            if not is_valid:
                return HttpResponse(
                    json.dumps({
                        "status": "failure",
                        "errorCode": "FileFormatError",
                        "lang": lang
                    }),
                    content_type="application/json"
                )

        # TODO round 精度差距
        try:
            turbo_calculation = TurboCalculation()
            pj = initiate_project(form.cleaned_data)

            # 初始化额定工况点
            initiate_rated_point(form.cleaned_data, pj, turbo_calculation)
            # 计算鼓风机的选择
            turbo_calculation.calculate_selected_turbo()

            # 获取测试点
            get_all_base_points(turbo_calculation, upload_data)

            # 获取普通工况点
            get_normal_points(form.cleaned_data, turbo_calculation)

            # 进行插值计算
            turbo_calculation.interpolation_calculation(10)

            # 获取最终返回数据
            final_table_data = turbo_calculation.get_all_data()
            final_data = {**final_table_data, **{
                "status": "success",
                "errorCode": "",
                "lang": lang
            }}
        except Exception as e:
            return HttpResponse(
                json.dumps({
                    "status": "failure",
                    "errorCode": "NoBlowerFitError",
                    "lang": lang,
                }),
                content_type="application/json"
            )

        return HttpResponse(
            json.dumps(final_data),
            content_type="application/json",
        )

class ExcelView(LoginRequiredMixin, View):
    def post(self, request, lang="cn"):
        filename = 'turbo_result.xlsx'
        if lang not in LANGUAGE:
            response = HttpResponse(
                "",
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename=%s' % filename
            return response

        post_data =  request.POST.get('excelValue')
        post_data = json.loads(post_data)
        table_data = post_data.get('tableData')

        output = io.BytesIO()

        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        # 向excel中添加表格
        add_table_to_excel(worksheet, workbook, table_data, lang)

        worksheet2 = workbook.add_worksheet()
        conditions = post_data.get("conditions")

        # 向excel中添加图表
        add_chart_to_excel(conditions, worksheet, worksheet2, workbook, lang)

        # Close the workbook before sending the data.
        workbook.close()

        # Rewind the buffer.
        output.seek(0)

        # Set up the Http response.
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response

class GetUserProjectsView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, lang="cn", user_id=1):
        user_record = UserProfile.objects.filter(pk=user_id)
        if lang not in LANGUAGE or not user_record:
            return render(request, '404.html')

        if request.user.id != user_id:
            return HttpResponseRedirect(reverse("user_projects", kwargs={"user_id": request.user.id}))
        projects = TurboProject.objects.filter(creator=user_id).order_by("-create_time")
        lang_urls = get_lang_url("user_projects", {"user_id": user_id})

        return render(request, 'user_project_list.html', {
            "lang":lang ,
            "user_id": user_id,
            "projects": projects,
            "langCategory": LANGUAGE,
            "langUrls": lang_urls
        })

class GetAllProjectsView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, lang="cn"):
        if lang not in LANGUAGE:
            return render(request, "404.html")
        projects = TurboProject.objects.all().order_by("-create_time")
        lang_urls = get_lang_url("all_projects", {})
        return render(request, 'project_list.html', {
            'lang': lang,
            'projects': projects,
            "langCategory": LANGUAGE,
            "langUrls": lang_urls
        })

class ProjectView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, lang="cn", project_id=1):
        project_record = TurboProject.objects.filter(pk=project_id)
        if lang not in LANGUAGE or not project_record:
            return render(request, '404.html')

        sizer_records = Sizer.objects.filter(project=project_id)
        for x in range(0, len(sizer_records)):
            sizer_records[x].sizer_index = x + 1
        lang_urls = get_lang_url("project", kwargs={"project_id": project_id})
        return render(request, 'project.html', {
            "lang": lang,
            'project': project_record[0],
            'sizers': sizer_records,
            "langCategory": LANGUAGE,
            "langUrls": lang_urls
        })

class CreateProjectView(LoginRequiredMixin, View):
    def get(self, request, lang="cn", user_id=1):
        user_record = UserProfile.objects.filter(pk=user_id)
        if lang not in LANGUAGE or not user_record:
            return render(request, "404.html")

        if request.user.id != user_id:
            return HttpResponseRedirect(reverse("create_project", kwargs={"lang": lang, "user_id": request.user.id}))
        lang_urls = get_lang_url("create_project", {"user_id": user_id})
        return render(request, 'project_create.html', {
            "lang": lang,
            "user_id": user_id,
            "langCategory": LANGUAGE,
            "langUrls": lang_urls
        })

    def post(self, request, lang="cn", user_id=1):
        user_record = UserProfile.objects.filter(pk=user_id)
        if lang not in LANGUAGE or not user_record:
            return HttpResponse(
                json.dumps(
                    {
                        "status": "failure",
                        "errorCode": "URLNotExist",
                        "lang": lang
                    }
                ),
                content_type="application/json"
            )
        if request.user.id != user_id:
            return HttpResponse(
                json.dumps(
                    {
                        "status": "failure",
                        "errorCode": "PermissionDenied",
                        "lang": lang,
                    }
                ),
                content_type="application/json"
            )
        form = ProjectForm(request.POST)
        if not form.is_valid():
            return HttpResponse(
                json.dumps(
                    {
                        "status": "failure",
                        "errorCode": "ParameterError",
                        "lang": lang,
                    }
                ),
                content_type="application/json"
            )
        try:
            with transaction.atomic():
                pj_name = form.cleaned_data["projectName"]
                pj_address = form.cleaned_data["projectAddress"]
                pj_index = form.cleaned_data["projectIndex"]
                pj_engineer = form.cleaned_data["projectEngineer"]
                project = TurboProject(
                    project_name=pj_name,
                    project_address=pj_address,
                    project_index=pj_index,
                    project_engineer=pj_engineer,
                    creator = UserProfile.objects.get(pk=user_id),
                    create_time = datetime.now()
                )
                project.save()
        except Exception as e:
            return HttpResponse(
                json.dumps(
                    {
                        "status": "failure",
                        "errorCode": "CreateProjectError",
                        "lang": lang
                    }
                ),
                content_type="application/json"
            )

        return HttpResponse(
            json.dumps(
                {
                    "status": "success",
                    "url": reverse("user_projects", kwargs={"user_id": user_id, "lang": lang}),
                    "errorCode": "",
                    "lang": lang,
                }
            ),
            content_type="application/json"
        )

class DeleteProjectView(LoginRequiredMixin, View):

    def post(self, request, lang="cn", user_id=1, project_id=1):
        project_record = TurboProject.objects.filter(pk=project_id)
        if lang not in LANGUAGE or not project_record:
            return HttpResponse(
                json.dumps(
                    {
                        "status": "failure",
                        "errorCode": "URLNotExist",
                        "lang": lang
                    }
                ),
                content_type="application/json"
            )
        sizer_record = Sizer.objects.filter(project=project_record[0])
        try:
            with transaction.atomic():
                sizer_record.delete()
                project_record.delete()
        except Exception as e:
            return HttpResponse(
                json.dumps(
                    {
                        "status": "failure",
                        "errorCode": "DeleteProjectError",
                        "lang": lang
                    }
                ),
                content_type="application/json"
            )
        return HttpResponse(
            json.dumps({
                "status": "success",
                "url": reverse("user_projects", kwargs={"user_id": user_id, "lang": lang}),
                "errorCode": "",
                "lang": lang
            }),
            content_type="application/json"
        )

class EditProjectView(LoginRequiredMixin, View):
    login_url = "/login/"

    def post(self, request, lang="cn", project_id=1):
        project_record = TurboProject.objects.filter(pk=project_id)
        if lang not in LANGUAGE or not project_record:
            return HttpResponse(
                json.dumps(
                    {
                        "status": "failure",
                        "errorCode": "URLNotExist",
                        "lang": lang
                    }
                ),
                content_type="application/json"
            )

        project = project_record[0]
        if request.user.id != project.creator.id:
            return HttpResponse(
                json.dumps(
                    {
                        "status": "failure",
                        "errorCode": "PermissionDenied",
                        "lang": lang
                    }
                ),
                content_type="application/json"
            )
        form = ProjectForm(request.POST)
        if not form.is_valid():
            return HttpResponse(
                json.dumps(
                    {
                        "status": "failure",
                        "errorCode": "ParameterError",
                        "lang": lang,
                    }
                ),
                content_type="application/json"
            )
        try:
            with transaction.atomic():
                project.project_name = form.cleaned_data["projectName"]
                project.project_address = form.cleaned_data["projectAddress"]
                project.project_index = form.cleaned_data["projectIndex"]
                project.project_engineer = form.cleaned_data["projectEngineer"]

                project.save()

        except Exception as e:
            return HttpResponse(
                json.dumps(
                    {
                        "status": "failure",
                        "errorCode": "EditProjectError",
                        "lang": lang,
                    }
                ),
                content_type="application/json"
            )
        return HttpResponse(
            json.dumps(
                {
                    "status": "success",
                    "url": reverse("project", kwargs={"project_id": project_id, "lang": lang}),
                    "errorCode": "",
                    "lang": lang
                }
            ),
            content_type="application/json"
        )

class CreateSizerView(LoginRequiredMixin, View):

    def get(self, request, lang="cn", project_id=1):
        project_record = TurboProject.objects.filter(pk=project_id)
        if lang not in LANGUAGE or not project_record:
            return render(request, "404.html")

        lang_urls = get_lang_url("sizer_create", {"project_id": project_id})
        return render(request, 'sizer_create.html', {
            "lang": lang,
            "project_id": project_id,
            "langCategory": LANGUAGE,
            "langUrls": lang_urls
        })

    def post(self, request, lang="cn", project_id=1):

        project_record = TurboProject.objects.filter(pk=project_id)
        if lang not in LANGUAGE or not project_record:
            return HttpResponse(
                json.dumps(
                    {
                        "status": "failure",
                        "errorCode": "URLNotExist",
                        "lang": lang
                    }
                ),
                content_type="application/json"
            )

        form = SelectionForm(request.POST)
        # 数据验证
        if not form.is_valid():
            return HttpResponse(
                json.dumps({
                    "status": "failure",
                    "errorCode": "ParameterError",
                    "lang": lang
                }),
                content_type="application/json"
            )
        turbo_conditiona_array = form.cleaned_data.get('workingConditions', [])
        turbo_conditiona_array = json.dumps(turbo_conditiona_array)
        try:
            with transaction.atomic():
                turbo = Sizer(
                    creator = request.user,
                    project = project_record[0],
                    create_time = datetime.now(),
                    update_time = datetime.now(),
                    is_imperial = get_is_imperial(form.cleaned_data),
                    altitude = float(form.cleaned_data.get("projectAltitude")),
                    inlet_press = float(form.cleaned_data.get("projectInletPres")),
                    frequency_select = int(form.cleaned_data.get("frequencySelect")),
                    units_num = int(form.cleaned_data.get("projectUnitsNum")),
                    volt = int(form.cleaned_data.get("projectVolt")),
                    material = form.cleaned_data.get("projectMaterial"),
                    safety_factor = float(form.cleaned_data.get("projectSafetyFactor")),
                    ei_rating = float(form.cleaned_data.get("projectEIRating")),
                    env_temp = float(form.cleaned_data.get("projectEnvTemp")),
                    rating_flow = float(form.cleaned_data.get("ratingFlow")),
                    rating_pressure = float(form.cleaned_data.get("ratingPressure")),
                    rating_temp = float(form.cleaned_data.get("ratingTemp")),
                    rating_humi = float(form.cleaned_data.get("ratingHumi")),
                    rating_point_inlet_pressure = float(form.cleaned_data.get("ratingPointInletPressure")),
                    rating_point_inlet_temp = float(form.cleaned_data.get("ratingPointInletTemp")),
                    rating_point_humi = float(form.cleaned_data.get("ratingPointHumi")),
                    rating_point_inlet_loss = float(form.cleaned_data.get("ratingPointInletLoss")),
                    rating_point_outlet_loss = float(form.cleaned_data.get("ratingPointOutletLoss")),
                    rating_point_out_pressure = float(form.cleaned_data.get("ratingPointOutPressure")),
                    max_flow_coeff = float(form.cleaned_data.get("maxFlowCoeff")),
                    max_pressure_coeff = float(form.cleaned_data.get("maxPressureCoeff")),
                    working_conditions = turbo_conditiona_array,
                )
                turbo.save()
        except Exception as e:
            return HttpResponse(
                json.dumps({
                    "status": "failure",
                    "errorCode": "CreateSizerError",
                    "lang": lang
                }),
                content_type="application/json"
            )
        return HttpResponse(
            json.dumps({
                "status": "success",
                "url": reverse("project", kwargs={"project_id": project_id, "lang": lang}),
                "errorCode": "",
                "lang": lang,
            }),
            content_type="application/json"
        )

class SizerView(LoginRequiredMixin, View):
    def get(self, request, lang="cn", sizer_id=1):
        sizer_record = Sizer.objects.filter(pk=sizer_id)
        if lang not in LANGUAGE or not sizer_record:
            return render(request, "404.html")
        sizer_record[0].working_conditions = json.loads(sizer_record[0].working_conditions)
        lang_urls = get_lang_url("sizer", {"sizer_id": sizer_id})
        return render(request, "sizer_edit.html", {
            "lang": lang,
            "sizer": sizer_record[0],
            "langCategory": LANGUAGE,
            "langUrls": lang_urls
        })

class EditSizerView(LoginRequiredMixin, View):

    def post(self, request, lang="cn", sizer_id=1):
        sizer_record = Sizer.objects.filter(pk=sizer_id)
        if lang not in LANGUAGE or not sizer_record:
            return HttpResponse(
                json.dumps(
                    {
                        "status": "failure",
                        "errorCode": "URLNotExist",
                        "lang": lang
                    }
                ),
                content_type="application/json"
            )
        sizer = sizer_record[0]
        form = SelectionForm(request.POST)
        # 数据验证
        if not form.is_valid():
            return HttpResponse(
                json.dumps({
                    "status": "failure",
                    "errorCode": "ParameterError",
                    "lang": lang
                }),
                content_type="application/json"
            )
        try:
            with transaction.atomic():

                turbo_conditiona_array = form.cleaned_data.get('workingConditions', [])
                turbo_conditiona_array = json.dumps(turbo_conditiona_array)
                sizer.update_time = datetime.now()
                sizer.is_imperial = get_is_imperial(form.cleaned_data)
                sizer.altitude = form.cleaned_data.get("projectAltitude")
                sizer.inlet_press = form.cleaned_data.get("projectInletPres")
                sizer.frequency_select = form.cleaned_data.get("frequencySelect")
                sizer.units_num = form.cleaned_data.get("projectUnitsNum")
                sizer.volt = form.cleaned_data.get("projectVolt")
                sizer.material = form.cleaned_data.get("projectMaterial")
                sizer.safety_factor = form.cleaned_data.get("projectSafetyFactor")
                sizer.ei_rating = form.cleaned_data.get("projectEIRating")
                sizer.env_temp = form.cleaned_data.get("projectEnvTemp")
                sizer.rating_flow = form.cleaned_data.get("ratingFlow")
                sizer.rating_pressure = form.cleaned_data.get("ratingPressure")
                sizer.rating_temp = form.cleaned_data.get("ratingTemp")
                sizer.rating_humi = form.cleaned_data.get("ratingHumi")
                sizer.rating_point_inlet_pressure = form.cleaned_data.get("ratingPointInletPressure")
                sizer.rating_point_inlet_temp = form.cleaned_data.get("ratingPointInletTemp")
                sizer.rating_point_humi = form.cleaned_data.get("ratingPointHumi")
                sizer.rating_point_inlet_loss = form.cleaned_data.get("ratingPointInletLoss")
                sizer.rating_point_outlet_loss = form.cleaned_data.get("ratingPointOutletLoss")
                sizer.rating_point_out_pressure = form.cleaned_data.get("ratingPointOutPressure")
                sizer.max_flow_coeff = form.cleaned_data.get("maxFlowCoeff")
                sizer.max_pressure_coeff = form.cleaned_data.get("maxPressureCoeff")
                sizer.working_conditions = turbo_conditiona_array

                sizer.save()
        except Exception as e:
            return HttpResponse(
                json.dumps({
                    "status": "failure",
                    "errorCode": "EditSizerError",
                    "lang": lang
                }),
                content_type="application/json"
            )

        return HttpResponse(
            json.dumps({
                "status": "success",
                "url": reverse("sizer", kwargs={"sizer_id": sizer_id, "lang": lang}),
                "errorCode": "",
                "lang": lang
            }),
            content_type="application/json"
        )

class DeleteSizerView(LoginRequiredMixin, View):

    def post(self, request, lang="cn", sizer_id=1):
        sizer_record = Sizer.objects.filter(pk=sizer_id)
        if lang not in LANGUAGE or not sizer_record:
            return HttpResponse(
                json.dumps(
                    {
                        "status": "failure",
                        "errorCode": "URLNotExist",
                        "lang": lang
                    }
                ),
                content_type="application/json"
            )
        project_id = sizer_record[0].project.id
        try:
            with transaction.atomic():
                sizer_record.delete()
        except Exception as e:
            return HttpResponse(
                json.dumps(
                    {
                        "status": "failure",
                        "errorCode": "DeleteSizerError",
                        "lang": lang
                    }
                ),
                content_type="application/json"
            )
        return HttpResponse(
            json.dumps({
                "status": "success",
                "url": reverse("project", kwargs={"project_id": project_id, "lang": lang}),
                "errorCode": "",
                "lang": lang
            }),
            content_type="application/json"
        )
