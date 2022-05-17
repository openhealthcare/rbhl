angular.module("opal.controllers").controller("OCCLDHelper", function(
	$scope
) {
	/*
	A helper for the occld episode category screen
	*/

	var self = this;

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

})
