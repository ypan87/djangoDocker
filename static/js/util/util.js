/**
 * Created by yifan_pan on 2019/10/14.
 */
import axios from "axios";

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
