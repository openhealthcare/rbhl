angular
  .module("opal.controllers")
  .controller("DeleteEpisodeCtrl", function(
    $scope, $http, $window, $q, episode, $modalInstance, callBack
  ) {
    "use strict";
		$scope.episode = episode;

		var url = '/indigo/v0.1/occld_episode/';
		$scope.delete = function(){
			$http.delete(url + $scope.episode.id + "/").then(
				function() {
					$q.when(callBack()).then(function(){
						$modalInstance.close();
					})
				},
				function(response) {
				$window.alert('Patient could not be deleted');
			});
		}

		$scope.cancel = function() {
			$modalInstance.close('cancel');
		};
	});
