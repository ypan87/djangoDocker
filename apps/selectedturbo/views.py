import json
import xlsxwriter
import io
from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .services.project import Project
from .services.design_points import RatedPoint, DutyPoint
from .services.base_points import BasePoint
from .services.turbo_data import TurboData
from .services.turbo_calculation import *
from .forms import SelectionForm
from .forms import ProjectForm
from .models import Turbo, TestPoints, Sizer
from .models import Project as TurboProject
from users.models import UserProfile

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

def get_all_base_points(turbo_calculation, category="GL3"):
    base_points_collection = []
    for x in range(1, 12):
        condition_collection = []
        for y in range (1, 9):
            point_set = TestPoints.objects.filter(working_condition=x, working_position=y)[:1]
            for point in point_set:
                base_point = BasePoint(point)
                condition_collection.append(base_point)
        base_points_collection.append(condition_collection)
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

def add_chart_to_excel(conditions, worksheet, worksheet2, workbook):
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

def add_table_to_excel(worksheet, workbook, table_data):
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
                       "风机型号：%s" % table_data.get("turbo"),
                       "%sC/%s%%" % (condition.get("temp"), condition.get("humidity")),
                   ],
                   [
                       "进气压力",
                       "%s bara" % condition.get("baraPressure"),
                   ],
                   [
                       "相对流量",
                       "ΔP",
                       "流量",
                       "轴功率",
                       "进线功率"
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

class CreateSizerView(LoginRequiredMixin, View):

    def get(self, request, project_id=1):
        project_record = TurboProject.objects.filter(pk=project_id)
        if project_record:
            return render(request, 'sizer_create.html', {"project_id": project_id})
        else:
            return render(request, "404.html")

    def post(self, request, project_id=1):
        # 验证project
        project_record = TurboProject.objects.filter(pk=project_id)

        if project_record:
            form = SelectionForm(request.POST)
            # 数据验证
            if form.is_valid():
                turbo_conditiona_array = form.cleaned_data.get('workingConditions', [])
                turbo_conditiona_array = json.dumps(turbo_conditiona_array)
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
                return HttpResponse(
                    json.dumps({
                        "status": "success",
                        "url": reverse("project", kwargs={"project_id": project_id}),
                        "errorCode": ""
                    }),
                    content_type="application/json"
                )

            else:
                return HttpResponse(
                    json.dumps({
                        "status": "failure",
                        "errorCode": "ParameterError"
                    }),
                    content_type="application/json"
                )

        else:
            return HttpResponse(
                json.dumps({
                    "status": "failure",
                    "errorCode": "RequestError"
                }),
                content_type="application/json"
            )

class CheckBlowerView(LoginRequiredMixin, View):
    def post(self, request):
        # 数据验证
        form = SelectionForm(request.POST)

        if form.is_valid():
            # TODO round 精度差距
            turbo_calculation = TurboCalculation()
            pj = initiate_project(form.cleaned_data)

            # 初始化额定工况点
            initiate_rated_point(form.cleaned_data, pj, turbo_calculation)
            # 计算鼓风机的选择
            turbo_calculation.calculate_selected_turbo()

            # 获取测试点
            get_all_base_points(turbo_calculation)

            # 获取普通工况点
            get_normal_points(form.cleaned_data, turbo_calculation)

            # 进行插值计算
            turbo_calculation.interpolation_calculation(10)

            # 获取最终返回数据
            final_table_data = turbo_calculation.get_all_data()

            return HttpResponse(
                json.dumps(final_table_data),
                content_type="application/json",
            )
        else:
            return HttpResponse(
                json.dumps({
                    "status": "failure",
                    "errorCode": "ParameterError"
                }),
                content_type="application/json"
            )

class ExcelView(LoginRequiredMixin, View):
    def post(self, request):
        post_data =  request.POST.get('excelValue')
        post_data = json.loads(post_data)
        table_data = post_data.get('tableData')

        output = io.BytesIO()

        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        # 向excel中添加表格
        add_table_to_excel(worksheet, workbook, table_data)

        worksheet2 = workbook.add_worksheet()
        conditions = post_data.get("conditions")

        # 向excel中添加图表
        add_chart_to_excel(conditions, worksheet, worksheet2, workbook)

        # Close the workbook before sending the data.
        workbook.close()

        # Rewind the buffer.
        output.seek(0)

        # Set up the Http response.
        filename = 'turbo_result.xlsx'
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename

        return response

# 返回图表需要的数据
class GetGraphDataView(LoginRequiredMixin, View):
    def post(self, request):
        # 数据验证
        form = SelectionForm(request.POST)

        if form.is_valid():

            # TODO round 精度差距
            turbo_calculation = TurboCalculation()
            pj = initiate_project(form.cleaned_data)

            # 初始化额定工况点
            initiate_rated_point(form.cleaned_data, pj, turbo_calculation)
            # 计算鼓风机的选择
            turbo_calculation.calculate_selected_turbo()

            # 获取测试点
            get_all_base_points(turbo_calculation)

            # 获取普通工况点
            get_normal_points(form.cleaned_data, turbo_calculation)

            # 进行插值计算
            turbo_calculation.interpolation_calculation(10)

            # 获取最终返回数据
            final_table_data = turbo_calculation.get_all_data()

            return HttpResponse(
                json.dumps(final_table_data),
                content_type="application/json",
            )
        else:
            pass

class CreateProjectView(LoginRequiredMixin, View):
    def get(self, request, user_id=1):
        user_record = UserProfile.objects.filter(pk=user_id)
        if user_record:
            return render(request, 'project_create.html', {"user_id": user_id})
        else:
            return render(request, '404.html')

    def post(self, request, user_id=1):
        user_record = UserProfile.objects.filter(pk=user_id)
        if user_record:
            if request.user.id != user_id:
                return HttpResponse(
                    json.dumps(
                        {
                            "status": "failure",
                            "errorCode": "PermissionDenied"
                        }
                    ),
                    content_type="application/json"
                )

            form = ProjectForm(request.POST)
            if form.is_valid():
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

                return HttpResponse(
                    json.dumps(
                        {
                            "status": "success",
                            "url": reverse("users:user_projects", kwargs={"user_id": user_id}),
                            "errorCode": ""
                        }
                    ),
                    content_type="application/json"
                )
            else:
                return HttpResponse(
                    json.dumps(
                        {
                            "status": "failure",
                            "errorCode": "ParameterError"
                        }
                    ),
                    content_type="application/json"
                )
        else:
            return HttpResponse(
                json.dumps(
                    {
                        "status": "failure",
                        "errorCode": "RequestError"
                    }
                ),
                content_type="application/json"
            )

class GetUserProjectsView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, user_id=1):
        user_record = UserProfile.objects.filter(pk=user_id)
        if user_record:
            # 如果用户访问的不是自己的主页，则导向自己的主页
            if request.user.id != user_id:
                return HttpResponseRedirect(reverse("users:user_projects", kwargs={"user_id": request.user.id}))
            projects = TurboProject.objects.filter(creator=user_id).order_by("-create_time")
            return render(request, 'user_project_list.html', {"user_id": user_id, "projects": projects})
        else:
            return render(request, "404.html")

class GetAllProjectsView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request):
        projects = TurboProject.objects.all().order_by("-create_time")
        return render(request, 'project_list.html', {'projects': projects})

class ProjectView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, project_id=1):
        project_record = TurboProject.objects.filter(pk=project_id)
        if project_record:
            sizer_records = Sizer.objects.filter(project=project_id)
            for x in range(0, len(sizer_records)):
                sizer_records[x].sizer_index = x + 1
            return render(request, 'project.html', {'project': project_record[0], 'sizers': sizer_records})
        else:
            return render(request, "404.html")

class EditProjectView(LoginRequiredMixin, View):
    login_url = "/login/"

    def post(self, request, project_id=1):
        project_record = TurboProject.objects.filter(pk=project_id)
        if project_record:
            project = project_record[0]
            if request.user.id != project.creator.id:
                return HttpResponse(
                    json.dumps(
                        {
                            "status": "failure",
                            "errorCode": "PermissionDenied"
                        }
                    ),
                    content_type="application/json"
                )

            form = ProjectForm(request.POST)
            if form.is_valid():
                project.project_name = form.cleaned_data["projectName"]
                project.project_address = form.cleaned_data["projectAddress"]
                project.project_index = form.cleaned_data["projectIndex"]
                project.project_engineer = form.cleaned_data["projectEngineer"]

                project.save()

                return HttpResponse(
                    json.dumps(
                        {
                            "status": "success",
                            "url": reverse("project", kwargs={"project_id": project_id}),
                            "errorCode": ""
                        }
                    ),
                    content_type="application/json"
                )
            else:
                return HttpResponse(
                    json.dumps(
                        {
                            "status": "failure",
                            "errorCode": "ParameterError"
                        }
                    ),
                    content_type="application/json"
                )
        else:
            return HttpResponse(
                json.dumps(
                    {
                        "status": "failure",
                        "errorCode": "RequestError"
                    }
                ),
                content_type="application/json"
            )

class SizerView(LoginRequiredMixin, View):
    def get(self, request, sizer_id=1):
        sizer_record = Sizer.objects.filter(pk=sizer_id)
        if sizer_record:
            sizer_record[0].working_conditions = json.loads(sizer_record[0].working_conditions)
            return render(request, "sizer_edit.html", {"sizer": sizer_record[0]})
        else:
            return render(request, "404.html")

class EditSizerView(View):
    def post(self, request, sizer_id=1):
        sizer_record = Sizer.objects.filter(pk=sizer_id)
        if sizer_record:
            sizer = sizer_record[0]
            form = SelectionForm(request.POST)
            # 数据验证
            if form.is_valid():
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
                return HttpResponse(
                    json.dumps({
                        "status": "success",
                        "url": reverse("sizer", kwargs={"sizer_id": sizer_id}),
                        "errorCode": ""
                    }),
                    content_type="application/json"
                )
            else:
                return HttpResponse(
                    json.dumps({
                        "status": "failure",
                        "errorCode": "ParameterError"
                    }),
                    content_type="application/json"
                )
        else:
            return HttpResponse(
                json.dumps(
                    {
                        "status": "failure",
                        "errorCode": "RequestError"
                    }
                ),
                content_type="application/json"
            )

