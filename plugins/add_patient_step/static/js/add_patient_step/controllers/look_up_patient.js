angular.module('opal.controllers').controller('LookupPatientCrl',
  function(scope, step, DemographicsSearch, $location) {
    "use strict";

    scope.lookup_hospital_number = function() {
      DemographicsSearch.find(
        step.search_end_point,
        scope.editing.demographics.hospital_number,
        {
            // we can't find the patient on either elicd or the hospital demographcis
            patient_not_found:    scope.new_patient,
            // the patient has been entered into elcid before
            patient_found_in_application: scope.new_for_patient,
            // the patient exists on the intrahospital api, but not in elcid
            patient_found_upstream: scope.new_for_patient
        });
    };

    this.initialise = function(scope){
      if($location.search().hospital_number){
        scope.editing.demographics = {
          hospital_number: $location.search().hospital_number
        };
        scope.lookup_hospital_number();
      }
      else{
        scope.state = 'initial';
        scope.editing.demographics = {
          hospital_number: undefined
        };
      }
      scope.hideFooter = true;
    };

    scope.new_patient = function(result){
        scope.hideFooter = false;
        scope.state = 'editing_demographics';
    };

    scope.new_for_patient = function(patient){
        var allTags = [];
        _.each(patient.episodes, function(episode){
          _.each(_.keys(episode.tagging[0]), function(tag){
            if(scope.metadata.tags[tag]){
              allTags.push(tag);
            }
          });
        });
        scope.allTags = _.uniq(allTags);
        scope.editing.demographics = patient.demographics[0]
        scope.state   = 'has_demographics';
        scope.hideFooter = false;
    };
    scope.showNext = function(editing){
        var nextStates = [
          "has_demographics",
          "editing_demographics",
        ]
        return nextStates.indexOf(scope.state) !== -1
    };

    scope.preSave = function(editing){
        // this is not great
        if(editing.demographics && editing.demographics.patient_id){
          scope.pathway.save_url = scope.pathway.save_url + "/" + editing.demographics.patient_id;
        }
    };
    this.initialise(scope);
});
