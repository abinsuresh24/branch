odoo.define("web_responsive.test_patch", function (require) {
    "use strict";

    const utils = require("web_tour.TourStepUtils");

    utils.include({
        showAppsMenuItem() {
            return {
                edition: "community",
                trigger: ".o_navbar_apps_menu",
                auto: true,
                position: "bottom",
            };
        },
    });
});
