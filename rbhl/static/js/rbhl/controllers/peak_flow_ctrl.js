angular
  .module("opal.controllers")
  .controller("PeakFlowCtrl", function($scope, PeakFlowGraphDataLoader, $routeParams) {
    "use strict";
    // split the peak flow by trial numbers
    $scope.graphDataByPeakFlowNum = {};
    $scope.trialNums = [];

    // used by the graph full page view
    if($routeParams.trial_num){
      $scope.trialNum = $routeParams.trial_num;
    }
    // highlights notes when you mouse over
    $scope.highlights = {}

    $scope.isFromPeakFlowDB = function(trial_num){
      var trialNum = parseInt(trial_num);
      var result = _.findWhere($scope.episode.imported_from_peak_flow_database, {
        trial_number: trialNum
      });
      return result;
    }

    var loadData = function(){
      PeakFlowGraphDataLoader.load($scope.episode.id).then(function(data){
        $scope.graphDataByPeakFlowNum = data.by_trial
        $scope.trialNums = data.order;

        $scope.trialNums.forEach(trialNum=> {
          $scope.highlights[trialNum] = {day_num: null};
        });

        // calculate what trial number to use when creating a new peak flow day trial
        // trial nums are a strings because they're object keys so translate them
        if($scope.trialNums.length){
          let trialNums = $scope.trialNums.map(trialNum => parseInt(trialNum))
          $scope.newTrialNum = Math.max(...trialNums) + 1;
        }
        else{
          $scope.newTrialNum = 1;
        }
      });
    }

    loadData();
  });
