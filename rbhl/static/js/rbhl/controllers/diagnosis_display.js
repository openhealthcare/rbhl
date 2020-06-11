angular.module('opal.controllers').controller('DiagnosisDisplay', function($scope) {
  "use strict";

  this.open_modal = function(templateName){
    var toResolve =  {
      item: function() { return item; },
      profile: profile,
      episode: function() { return episode; },
      metadata: function(Metadata) { return Metadata.load(); },
      referencedata: function(Referencedata){ return Referencedata.load(); }
    }
    $scope.open_modal('EditItemCtrl', templateName, toResolve)
  }

  this.isNAD = function(episode){
    var hasAsthma = episode.asthma.length;
    var hasRhinitis = episode.rhinitis.length;
    var hasChronicAirFlowLimitation = episode.chronic_air_flow_limitation.length;
    var hasMalignancy = episode.malignancy.length;
    var hasDiffuseLungDisease = episode.diffuse_lung_disease.length;
    var hasBenignPleuralDisease = episode.benign_pleural_disease.length;
    var hasOtherDiagnosis = _.filter(episode.other_diagnosis, function(d){
      d.diagnosis_type !== 'NAD'
    }).length;
    var result = hasAsthma || hasRhinitis || hasChronicAirFlowLimitation || hasMalignancy || hasDiffuseLungDisease || hasBenignPleuralDisease || hasOtherDiagnosis
    return !result;
  }
});
