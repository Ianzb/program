function copyString(string) {
    var input = document.createElement("input");
    input.value = string;
    document.body.appendChild(input);
    input.select();
    document.execCommand("copy");
    document.body.removeChild(input);
}