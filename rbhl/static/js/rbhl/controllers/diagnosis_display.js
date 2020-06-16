angular.module('opal.controllers').controller('DiagnosisDisplay', function(scope, $http) {
  "use strict";
  var self = this;
  this.hasNAD = false

  this.checkNAD = function(){
    $http.get("/api/v0.1/episode/" + scope.episode.id + "/").then(function(e){
      self.hasNAD = _.findWhere(e.diagnosis, {category: "NAD"});
    });
  }

  scope.$watch("episode.asthma_details", function(){
    self.checkNAD();
  }, true);

  scope.$watch("episode.rhinitis_details", function(){
    self.checkNAD();
  }, true);

  scope.$watch("episode.diagnosis", function(){
    self.checkNAD();
  }, true);
})