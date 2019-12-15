function BaseContent() {}

BaseContent.prototype.load = function() {
};
BaseContent.prototype.unload = function() {};

function Dashboard() {
    BaseContent.call(this);
}

Dashboard.prototype = Object.create(BaseContent.prototype);

Object.defineProperty(Dashboard.prototype, 'constructor', {
    value: Dashboard,
    enumerable: false, // so that it does not appear in 'for in' loop
    writable: true });

function SampleEditor() {
    BaseContent.call(this);
}

SampleEditor.prototype = Object.create(BaseContent.prototype);

Object.defineProperty(SampleEditor.prototype, 'constructor', {
    value: SampleEditor,
    enumerable: false, // so that it does not appear in 'for in' loop
    writable: true });

SampleEditor.prototype.load = function(state) {
    BaseContent.prototype.load.call(this);      // <- this is where the AJAX call to load the sample should take place

};


function ContentManager() {
    // add event handler for history
    window.addEventListener("popstate", function (event) {
        if(event.state != null) {
            if(!this.restoreState(event.state))     // e.g. if the user wants to stay on the page
                window.history.pushState(this.state, "", this.url);
        } else
            location.href = "/";
    });
}

ContentManager.protoype = {
    loadState: function (state) {
        switch(state.mode) {
            case "dashboard":
                break;
            case "sampleeditor":
                break;
            case "searchresults":
                break;
        }
    }
};

let CM = ContentManager();

$(document).ready(function () {
    CM.loadState(state);
});