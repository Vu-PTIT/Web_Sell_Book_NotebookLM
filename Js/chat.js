$(document).ready(function() {
    $("#messageArea").on("submit", function(event) {
        const date = new Date();
        const hour = date.getHours();
        const minute = date.getMinutes();
        const str_time = hour+":"+minute;
        var rawText = $("#text").val();
        var userHtml = '<div class="d-flex justify-content-end mb-4">' +
                        '<div class="msg_cotainer_send">' + rawText +
                            '<span class="msg_time_send">' + str_time + '</span>' +
                        '</div>' +
                        '<div class="img_cont_msg">' +
                            '<img src="https://i.ibb.co/d5b84Xw/Untitled-design.png" class="rounded-circle user_img_msg">' +
                        '</div>' +
               '</div>';
        $("#text").val("");
        $("#messageFormeight").append(userHtml);
        $.ajax({
            data: {
                msg: rawText,	
            },
            type: "POST",
            url: "/get",
        }).done(function(data) {
            var botHtml = '<div class="d-flex justify-content-start mb-4">' +
                                '<div class="img_cont_msg">' +
                                    '<img src="https://cdn-icons-png.flaticon.com/512/4712/4712035.png" class="rounded-circle user_img_msg">' +
                                '</div>' +
                                '<div class="msg_cotainer">' + data +
                                    '<span class="msg_time">' + str_time + '</span>' +
                                '</div>' +
                            '</div>';
            $("#messageFormeight").append($.parseHTML(botHtml));
        });
        event.preventDefault();
    });
});
$("#uploadForm").on("submit", function (e) {
    e.preventDefault();
    var formData = new FormData(this);

    $.ajax({
        url: "/upload",
        type: "POST",
        data: formData,
        success: function (res) {
            $("#uploadStatus").text(res.message);
        },
        cache: false,
        contentType: false,
        processData: false
    });
});
$("#fileInput").on("change", function () {
    const file = this.files[0];
    const previewContainer = $("#filePreviewContainer");
    const display = $("#fileNameDisplay");
    previewContainer.empty();
    display.empty();
    if (!file) return;
    const fileName = file.name;
    const isImage = file.type.startsWith("image/");
    if (isImage) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const img = $("<img>").attr("src", e.target.result);
            previewContainer.append(img);
        };
        reader.readAsDataURL(file);
    } else {
        const filePreview = $(`
            <div class="file-preview-wrapper">
                <img src="https://cdn-icons-png.flaticon.com/512/337/337946.png" alt="File icon">
                <span>${fileName}</span>
            </div>
        `);
        previewContainer.append(filePreview);

    }
});