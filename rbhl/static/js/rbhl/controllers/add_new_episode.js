angular.module('opal.controllers').controller('ConfirmAddNewEpisode', function($modalInstance, toMomentFilter, $scope, $http, patient, refresh) {
	"use strict";

	var fields = [
		"occld",
		"date_of_referral",
		"clinic_date",
		"referrer_name",
		"employer"
	]

	$scope.patient = patient;
	$scope.editing = {}

	$scope.clean = function(){
		_.each(fields, function(field){
			if(field !== 'occld'){
				$scope.editing[field] = null;
			}
		});
	}

	$scope.close = function(){
		$modalInstance.close();
	}

	$scope.save = function(){
		var data = {patient_id: patient.id}
		_.each(fields, function(field){
			if(_.isDate($scope.editing[field])){
				var fieldResult = toMomentFilter($scope.editing[field])
				if(fieldResult){
					data[field] = fieldResult.format('DD/MM/YYYY')
				}
			}
			else{
				data[field] = $scope.editing[field];
			}
		})
		$http.post('/indigo/v0.1/new_episode/', data).then(function(){
			refresh().then(function(){
				$scope.close();
			});
		});
	}
});
