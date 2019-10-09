/**
 * Created by yifan_pan on 2019/9/19.
 */
var baseController = (function() {

    var getCookie = function(name) {
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

    var Requester = function(url, data) {
        this.data = data;
        this.url = url;
    };

    Requester.prototype.ajaxRequest = function() {
        var self = this;

        return new Promise(function(resolve, reject) {
            $.ajax({
                cache: false,
                type: 'POST',
                url: self.url,
                headers:{ "X-CSRFtoken": getCookie('csrftoken')},
                data: self.data,
                async: true,
                beforeSend:function (xhr,settings) {
                },
                success: function(data) {
                    resolve(data);
                },
                error: function(jqXHR, textStatus, errorThrown) {
                }
            });
        });
    };

    return {
        createRequester: function(url, data) {
            return new Requester(url, data);
        },

    }
})();

var baseView = (function() {
    var DOMs = {
        table: document.querySelector("#projects"),
        confirmDeleteBtn: document.querySelector(".confirm-delete"),
    };

    var DOMStrings = {
        deleteModal: "deleteModal"
    };

    return {
        getDOMs: function() {
            return DOMs;
        },
        getDOMStrings: function() {
            return DOMStrings;
        },
        getLang: function() {
            return window.location.pathname.split('/')[1];
        },
    }
})();

var controller = (function(baseView, baseCtrl) {
    var DOMs = baseView.getDOMs();
    var DOMStrings = baseView.getDOMStrings();
    var lang = baseView.getLang();

    var setupEventListeners = function() {
        DOMs.table.addEventListener("click", function(event) {
            if (event.target.matches('.delete')) {
                showDeleteTipModal();
                var url = event.target.dataset.url;
                DOMs.confirmDeleteBtn.addEventListener("click", function(e) {
                    var requester = baseCtrl.createRequester(url, "");
                    var promise = requester.ajaxRequest();
                    promise.then(function(result) {
                        hideDeleteTipModal();
                        if (result.status == "success") {
                            toastr.options = {
                                timeOut: toastr_time["success"],
                                positionClass: 'toast-top-right',
                                onHidden: function() {window.location.href=result.url}
                            };
                            toastr.success(
                                errorCode[lang]["deleteProjectSuccess"]
                            );
                        } else if (result.status == "failure") {
                            toastr.options = {
                                timeOut: toastr_time["danger"],
                                positionClass: 'toast-top-right'
                            };
                            toastr.error(
                                errorCode[lang][result.errorCode]
                            );
                        }
                    });
                })
            }
        });
    };

    var showDeleteTipModal = function() {
        $(`#${DOMStrings.deleteModal}`).modal('show');
    };

    var hideDeleteTipModal = function() {
        $(`#${DOMStrings.deleteModal}`).modal('hide');
    };

    var setupTables = function() {
        $(document).ready(function() {
            $('#projects').DataTable();
        });
    };

    return {
        init: function() {
            setupEventListeners();
            setupTables();
        }
    }
})(baseView, baseController);

controller.init();