(function ($) {
    "use strict";

    $("[data-toggle='tooltip']").tooltip();

    $(document).ready(function () {
        $('.toast').toast('show');
    });

})(jQuery);