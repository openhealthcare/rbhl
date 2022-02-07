angular
  .module("opal.controllers")
  .controller("DeletePatientCtrl", function(
    $scope, $http, $window, $location, patient, $modalInstance
  ) {
    "use strict";

		var url = '/indigo/v0.1/delete_patient/';

		function getRandomInt(max) {
			return Math.floor(Math.random() * max);
		}

		$scope.patient = patient
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

		$scope.deletePatient = function(){
			$http.delete(url + $scope.patient.id + "/").then(
				function() {
					$modalInstance.close();
					$location.path("/");
				},
				function(response) {
				$window.alert('Patient could not be deleted');
			});
		}

		$scope.cancel = function() {
			$modalInstance.close('cancel');
		};
	});
