angular
  .module("opal.controllers")
  .controller("DeleteEpisodeCtrl", function(
    $scope, $http, $window, $q, episode, $modalInstance, callBack
  ) {
    "use strict";
		function init(){
			$scope.episode = episode;
			$scope.is_populated = $scope.are_there_entries();
			$scope.peak_flow_day_count = $scope.get_peak_flow_day_count();
		}

		function getRandomInt(max) {
			return Math.floor(Math.random() * max);
		}

		$scope.mathCheck = {
			int1: getRandomInt(10),
			int2: getRandomInt(10),
			result: ""
		}

		$scope.answered = function(){
			var result = parseInt($scope.mathCheck.result);
			if(result && $scope.mathCheck.int1 + $scope.mathCheck.int2 === result){
				return true;
			}
		}

		$scope.get_peak_flow_day_count = function(){
			return _.uniq(_.pluck($scope.episode.peak_flow_day, "trial_num")).length
		}

		$scope.are_there_entries = function(){
			if(episode.employment[0].consistency_token){
				return true;
			}
			if(episode.social_history[0].consistency_token){
				return true;
			}
			if(episode.diagnosis.length){
				return true;
			}
			if(episode.action_log.length){
				return true;
			}
			if(episode.letter.length){
				return true
			}
			if(episode.peak_flow_day.length){
				return true
			}
			if(episode.clinic_log[0].consistency_token){
				return true;
			}
		}

		var url = '/indigo/v0.1/occld_episode/';
		$scope.delete = function(){
			$http.delete(url + $scope.episode.id + "/").then(
				function() {
					$q.when(callBack()).then(function(){
						$modalInstance.close();
					})
				},
				function(response) {
				$window.alert('Referral could not be deleted');
			});
		}

		$scope.cancel = function() {
			$modalInstance.close('cancel');
		};

		init();
	});
