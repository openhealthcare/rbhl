angular
  .module("opal.controllers")
  .controller("AddOCCLDEpisodeCtrl", function(
    $scope, $http, $window, $q, patient, $modalInstance, callBack
  ) {
    "use strict";
		/*
		* Adds a new episode and returns the if it is created
		*/
		$scope.patient = patient;

		var url = '/indigo/v0.1/occld_episode/';
		$scope.add = function(){
			$http.post(url, {patient_id: patient.id}).then(
				function(response) {
					$q.when(callBack()).then(function(){
						$modalInstance.close(response.data.id);
					})
				},
				function(response) {
				$window.alert('Referral could not be created');
			});
		}

		$scope.cancel = function() {
			$modalInstance.close();
		};
	});
