angular
  .module("opal.services")
  .factory("DemographicsSearchLookup", function($http, $window, ngProgressLite) {
    "use strict";
    /*
     * The demographics search used by the find patient
     * pathway.
     */

    // patient is found in indigo
    var PATIENTS_FOUND = "patient_found";

    // patient is not found
    var PATIENT_NOT_FOUND = "patient_not_found";

    var expectedStatuses = [
      PATIENTS_FOUND,
      PATIENT_NOT_FOUND
    ];

    var find = function(apiEndPoint, query, findPatientOptions) {
      ngProgressLite.set(0);
      ngProgressLite.start();
      var callBackNames = _.keys(findPatientOptions);
      _.each(callBackNames, function(key) {
        if (expectedStatuses.indexOf(key) === -1) {
          throw "unknown call back";
        }
      });
      var patientUrl = apiEndPoint + "?query=" + encodeURIComponent(query);
      $http.get(patientUrl).then(
        function(response) {
          var patientList = response.data.object_list;
          ngProgressLite.done();
          if(patientList.length){
            findPatientOptions[PATIENTS_FOUND](patientList, response.data.total_count);
          }
          else{
            findPatientOptions[PATIENT_NOT_FOUND]();
          }
        },
        function() {
          ngProgressLite.done();
          $window.alert("DemographicsSearchLookup could not be loaded");
        }
      );
    };

    return {
      find: find
    };
  });
