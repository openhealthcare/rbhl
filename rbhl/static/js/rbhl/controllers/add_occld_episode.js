angular
  .module("opal.controllers")
  .controller("AddOCCLDEpisodeCtrl", function(
    $scope, $http, $window, $q, patient, $modalInstance, callBack
  ) {
    "use strict";
		$scope.patient = patient;

		var url = '/indigo/v0.1/occld_episode/';
		$scope.add = function(){
			$http.post(url, {patient_id: patient.id}).then(
				function() {
					$q.when(callBack()).then(function(){
						$modalInstance.close();
					})
				},
				function(response) {
				$window.alert('Referral could not be created');
			});
		}

		$scope.cancel = function() {
			$modalInstance.close('cancel');
		};
	});
