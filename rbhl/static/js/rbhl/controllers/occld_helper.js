angular.module("opal.controllers").controller("OCCLDHelper", function(
	$scope, $modal
) {
	/*
	* A helper for the occld episode category screen
	*/

	var self = this;

	var init = function(){
		self.episodeIdsClinicData = [];
	}

	self.referralOrdering = function(episode){
		/*
		* Order the referrals by clinic date if it exists
		* otherwise use date of referral, or date of first appointment
		* if these are populated.
		*
		* If nothing is populated return a date in the future
		* so that they appear at the top
		*/
		var clinicDate = episode.clinic_log[0].clinic_date;
		if(clinicDate){
			return clinicDate;
		}
		var dateOfReferral = episode.referral[0].date_of_referral;
		if(dateOfReferral){
			return dateOfReferral;
		}
		var dateFirstAppointment = episode.referral[0].date_first_appointment;
		if(dateFirstAppointment){
			return dateFirstAppointment;
		}
		return moment(new Date(5000, 0, 0));
	}

	self.revealClinicData = function(episode){
		/*
		* Display the patient's clinic information
		* record panel.
		*/
		self.episodeIdsClinicData.push(episode.id);
	}

	self.showClinicInformation = function(episode){
		/*
		* returns true if we should show the clinical information
		* related to the patient
		*/
		if(_.indexOf(self.episodeIdsClinicData, episode.id) !== -1){
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

	self.addEpisode = function(patient){
		/*
		* Opens the add referral modal that requests confirmation that the
		* user would like to add the episode.
		*/
    $modal.open({
      templateUrl: '/templates/add_episode.html',
      controller: 'AddOCCLDEpisodeCtrl',
      resolve: {
        patient: patient,
				callBack: function(){
					return $scope.refresh;
				}
      }
		}).result.then(function(modalResult){
			if(modalResult){
				var episode = _.findWhere($scope.patient.episodes, {id: modalResult});
				episode.recordEditor.editItem(
					'referral',
					episode.referral[0]
				)
			}
		});
	}

	self.deleteEpisode = function(episode){
		/*
		* Opens the deletion modal that requests confirmation that the
		* user would like to delete the episode.
		*/
    $modal.open({
      templateUrl: '/templates/delete_episode.html',
      controller: 'DeleteEpisodeCtrl',
      resolve: {
        episode: episode,
				callBack: function(){
					return $scope.refresh;
				}
      }
    });
	}

	init();
})
