angular.module('opal.controllers').controller('DiagnosisDisplay', function($scope, $http) {
  "use strict";
  var self = this;

  this.refreshIfNAD = function(itemName){
    /*
    * Asthma details and rhinitis details create diagnosis
    * so to make it track easier, if we save either of these two
    * refresh the patient
    */
    if(itemName === 'asthma_details' || itemName === 'rhinitis_details'){
      $scope.refresh();
    }
    /*
    * Marking something as NAD removes all existing diagnosis
    *
    * Adding a diagnosis when the patient is NAD removes
    * the diagnosis of NAD
    *
    * So if either of these conditions is true, refresh the view after the
    * modal closes.
    */
    else if(itemName === "NAD" || _.findWhere($scope.episode.diagnosis, {category: "NAD"})){
      $scope.refresh();
    }
  }

  this.editItem = function(itemName, item, template){
    $scope.episode.recordEditor.editItem(itemName, item, template).then(function(){
      self.refreshIfNAD(itemName);
    });
  }

  this.newItem = function(itemName, template){
    $scope.episode.recordEditor.newItem(itemName, template).then(function(){
      self.refreshIfNAD(itemName);
    });
  }
})