angular.module("opal.services").factory("ClinicDateComparator", function() {
  "use strict";
  return [
    function(e) {
      return -e.clinic_log[0].clinic_date;
    }
  ];
});
