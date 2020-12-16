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

    scope.reset = function(){
      if(scope.patientList){
        scope.state = "patient_list";
        scope.hideFooter = true;
      }
      else{
        thisStep.initialise(scope);
      }
    }

    scope.new_patient = function() {
      scope.hideFooter = false;
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
