angular
  .module("opal.controllers")
  .controller("PeakFlowCtrl", function($scope, PeakFlowGraphDataLoader) {
    "use strict";
    // split the peak flow by trial numbers
    $scope.graphDataByPeakFlowNum = {};
    $scope.trialNums = [];

    // highlights notes when you mouse over
    $scope.highlights = {}

    PeakFlowGraphDataLoader.load($scope.episode.id).then(function(data){
      $scope.graphDataByPeakFlowNum = data
      $scope.trialNums = Object.keys($scope.graphDataByPeakFlowNum).sort().reverse();
      $scope.trialNums.forEach(trialNum=> {
        $scope.highlights[trialNum] = {day_num: null};
      });

      // calculate what trial number to use when creating a new peak flow day trial
      // trial nums are a strings because they're object keys so translate them
      if($scope.trialNums.length){
        var trialNums = $scope.trialNums.map(trialNum => parseInt(trialNum))
        $scope.newTrialNum = Math.max(...trialNums) + 1;
      }
      else{
        $scope.newTrialNum = 1;
      }
    });
  });
