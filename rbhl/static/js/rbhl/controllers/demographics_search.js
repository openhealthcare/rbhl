angular
  .module("opal.controllers")
  .controller("DemographicsSearchCtrl", function(
    scope,
    step,
    DemographicsSearchLookup
  ) {
    "use strict";

    var thisStep = this;

    scope.query = function() {
      scope.hideFooter = false;
      DemographicsSearchLookup.find(
        step.search_end_point,
        scope.search.query_term,
        {
          // we can't find the patient on either elicd or the hospital demographcis
          patient_not_found: scope.new_patient,
          // the patient has been entered into elcid before
          patient_found: scope.patients_found
        }
      );
    };

    this.initialise = function(scope) {
      scope.state = "initial";
      scope.search = {query_term: undefined};
      scope.hideFooter = true;
    };

    scope.back = function(){
      if(!scope.patientList || scope.state === "patient_list"){
        thisStep.initialise(scope);
      }
      else{
        scope.state = "patient_list";
      }
    }


    scope.new_patient = function() {
      scope.state = "editing_demographics";
    };

    scope.patients_found = function(patientList, count) {
      scope.count = count;
      scope.patientList = patientList
      scope.state = "patient_list";
    };

    scope.showNext = function(editing) {
      var nextStates = ["has_demographics", "editing_demographics"];
      return nextStates.indexOf(scope.state) !== -1;
    };

    this.initialise(scope);
  });
