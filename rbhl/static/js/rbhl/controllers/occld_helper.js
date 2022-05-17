angular.module("opal.controllers").controller("OCCLDHelper", function(
	$scope
) {
	/*
	A helper for the occld episode category screen
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
		self.episodeIdsClinicData.push(episode.id);
	}

	self.showClinicInformation = function(episode){
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
			return ture
		}
		if(episode.clinic_log[0].consistency_token){
			return true;
		}
	}

	init();
})
