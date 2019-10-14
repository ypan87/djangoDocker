/**
 * Created by yifan_pan on 2019/10/14.
 */
import {errorCode, toastrTime} from "./base";
import {Request, getLang} from "../util/util";
import {DOMs, DOMstrings} from "../user_project_list/views/userProjectListView";

// delete project
DOMs.table.addEventListener("click", function(event) {
    deleteProject(event.target);
});

const deleteProject = function(target) {
    if (target.matches('.delete')) {
        // show the modal to confirm
        showDeleteTipModal();
        let url = target.dataset.url;
        // send the request to delete project
        DOMs.confirmDeleteBtn.addEventListener("click", function(event) {
            sendDeleteRequest(url);
        });
    }
};

// send the request to delete project
const sendDeleteRequest = async function(url) {
    let lang = getLang();
    hideDeleteTipModal();
    let request = new Request(url, "");
    try {
        await request.getResults();
        let result = request.data;
        if (result.status == "success") {
            toastr.options = {
                timeOut: toastrTime.toastrTime["success"],
                positionClass: 'toast-top-right',
                onHidden: function() {window.location.href=result.url}
            };
            toastr.success(
                errorCode.errorCode[lang]["deleteProjectSuccess"]
            );
        } else if (result.status == "failure") {
            toastr.options = {
                timeOut: toastrTime.toastrTime["danger"],
                positionClass: 'toast-top-right'
            };
            toastr.error(
                errorCode.errorCode[lang][result.errorCode]
            );
        }
    } catch (err) {
        toastr.options = {
            timeOut: toastrTime.toastrTime["danger"],
            positionClass: 'toast-top-right'
        };
        toastr.error(
            errorCode.errorCode[lang]["NetworkError"]
        );
    }
};

// hide the modal
const showDeleteTipModal = function() {
    $(`#${DOMstrings.deleteModal}`).modal('show');
};

// show the modal
const hideDeleteTipModal = function() {
    $(`#${DOMstrings.deleteModal}`).modal('hide');
};

const setupTables = function() {
    $(document).ready(function() {
        $('#projects').DataTable();
    });
};

// setup the initial table
setupTables();


