angular
  .module("opal.controllers")
  .controller("PeakFlowCtrl", function($scope, PeakFlowGraphDataLoader) {
    "use strict";
    // split the peak flow by trial numbers
    $scope.graphDataByPeakFlowNum = {};
    $scope.trialNums = [];

    PeakFlowGraphDataLoader.load($scope.episode.id).then(function(data){
      $scope.graphDataByPeakFlowNum = data
      $scope.trialNums = Object.keys($scope.graphDataByPeakFlowNum).sort().reverse();
    });
  });
