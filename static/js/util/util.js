/**
 * Created by yifan_pan on 2019/10/14.
 */
import axios from "axios";
import {toastrTime} from "./toastrTime";
import {errorCode} from "./errorCode";

export class Request {
    constructor(url, data) {
        this.url = url;
        this.data = data;
    }

    async getResults() {
        let results = await axios.post(this.url, this.data, {
            headers:{ "X-CSRFtoken": getCookie('csrftoken')},
        });
        this.data = results.data;
    }
}

export const getLang = function() {
    return window.location.pathname.split('/')[1];
};

const getCookie = function(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};

export const renderLoading = function(elem) {
    if (elem.classList.contains('hidden')) {
        elem.classList.remove('hidden');
    }
};

export const removeLoading = function(elem) {
    if (!elem.classList.contains('hidden')) {
        elem.classList.add('hidden');
    }
};

export const renderBtnLoading = function(btn) {
    disableBtn(btn);
    let markup = `
        <div class="loading">
            <span></span>
            <span></span>
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    btn.textContent = "";
    btn.insertAdjacentHTML("afterbegin", markup);
};

export const removeBtnLoading = function(btn, text) {
    ableBtn(btn);
    btn.innerHTML = text;
};

export const disableBtn = function(btn) {
    btn.disabled = true;
};

export const ableBtn = function(btn) {
    btn.disabled = false;
};

export const clearFormInputError = function(input) {
    var inputError = input.parentElement.querySelector(".input-error");
    if (inputError) {
        inputError.innerHTML = '';
        if (!inputError.classList.contains('hidden')) {
            inputError.classList.add('hidden');
        }
    }
};

export const handleResponse = function(result, successCode="", lang="en") {
    if (result.status == "success") {
        if (result.url) {
            toastr.options = {
                timeOut: toastrTime["success"],
                positionClass: 'toast-top-right',
                onHidden: function() {window.location.href=result.url}
            };
        } else {
            toastr.options = {
                timeOut: toastrTime["success"],
                positionClass: 'toast-top-right',
            };
        }
        toastr.success(
            errorCode[lang][successCode]
        );
    } else if (result.status == "failure") {
        toastr.options = {
            timeOut: toastrTime["danger"],
            positionClass: 'toast-top-right'
        };
        toastr.error(
            errorCode[lang][result.errorCode]
        );
    }
};

export const unitSelectValue = function(selectElem) {
    return selectElem.options[selectElem.selectedIndex].value;
};