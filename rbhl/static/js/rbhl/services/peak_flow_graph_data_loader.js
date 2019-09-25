angular.module('opal.services').factory('PeakFlowGraphDataLoader', function($q, $http, $window) {
  "use strict";

  var url = '/indigo/v0.1/peak_flow_graph_data/';

  var load = function(episode_id, trial_num){
    var deferred = $q.defer();
    var graphUrl = url + episode_id + "/";
    $http.get(graphUrl).then(function(response) {
        deferred.resolve(response.data);
    }, function() {
      // handle error better
      $window.alert('Peak flow graph data could not be loaded');
    });
    return deferred.promise;
  };

  return {
    load: load
  };
});
