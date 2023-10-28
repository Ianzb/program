function iframeFullScreen() {
    var ifm = document.getElementByClass("iframe-full-screen");
    ifm.height = document.documentElement.clientHeight;
    ifm.width = document.documentElement.clientWidth;
}

function copyString(string) {
    var input = document.createElement("input");
    input.value = string;
    document.body.appendChild(input);
    input.select();
    document.execCommand("copy");
    document.body.removeChild(input);
}