filters.filter('testCount', function(displayDateFilter){
  return function(patient) {
    /*
    * We display tests by date, so a straight count does not
    * not make sense, especially for skin prick tests
    * where they are done as a set. So lets just do a
    * count of distinct test type dates
    *
    * Apart from other investigations where we consider them each to
    * be a different test type
    */
   var count = 0;
   _.each(["spirometry", "bronchial_test", "skin_prick_test", "blood_book"], function(testType){
     // date equality in js is awkward, casting it to a date handles nulls and gives us date
     // rather than datetime equality
     var dateField = "date";
     if(testType === 'blood_book'){
       dateField = "blood_date";
     }
     var displayDates = _.map(patient[testType], function(someTest){ return displayDateFilter(someTest[dateField])})
     var distinctDates = _.uniq(displayDates);
     count += distinctDates.length;
   });

   count += patient.other_investigations.length;

   return count;
  };
});