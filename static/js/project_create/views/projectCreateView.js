/**
 * Created by yifan_pan on 2019/10/14.
 */
export const DOMs = {
    form: document.querySelector('#projectForm'),
    loadIcon: document.querySelector('.wrapper'),
    createBtn: document.querySelector('button')
};

export const DOMstrings = {
    form: "projectForm"
};

export const URLs = {
    createProject: window.location.pathname,
};

export const renderLoading = function() {
    if (DOMs.loadIcon.classList.contains('hidden')) {
        DOMs.loadIcon.classList.remove('hidden');
    }
};

export const removeLoading = function() {
    if (!DOMs.loadIcon.classList.contains('hidden')) {
        DOMs.loadIcon.classList.add('hidden');
    }
};

export const disableCreateBtn = function() {
    DOMs.createBtn.disabled = true;
};

export const ableCreateBtn = function() {
    DOMs.createBtn.disabled = false;
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
