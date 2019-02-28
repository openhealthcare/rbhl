angular.module('opal.controllers').controller('PeakFlowCtrl', function ($scope, $timeout) {
  "use strict";
  // split the peak flow by trial numbers
  var peakFlowDaysBytrialNum = {}

  $scope.getIdx = function (pfd) {
    return $scope.episode.peak_flow_day.indexOf(pfd);
  }

  _.each($scope.episode.peak_flow_day, function (pfd) {
    var trialNum = String(pfd.trial_num);
    if (!peakFlowDaysBytrialNum[trialNum]) {
      peakFlowDaysBytrialNum[trialNum] = [];
    }

    peakFlowDaysBytrialNum[trialNum].push(pfd)
  });

  var trialNums = Object.keys(peakFlowDaysBytrialNum).sort().reverse()
  $scope.peakFlowDaysByTrial = [];

  _.each(trialNums, function (tn) {
    $scope.peakFlowDaysByTrial.push(peakFlowDaysBytrialNum[tn]);
  });
});