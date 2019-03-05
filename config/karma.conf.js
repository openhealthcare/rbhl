module.exports = function(config){
  var opalPath = process.env.OPAL_LOCATION;
  var karmaDefaults = require(opalPath + '/opal/tests/js_config/karma_defaults.js');
  var baseDir = __dirname + '/..';
  var coverageFiles = [
    // __dirname + '/../rbhl/assets/js/rbhl/*',
    // __dirname + '/../rbhl/assets/js/rbhl/controllers/*',
    // __dirname + '/../rbhl/assets/js/rbhl/services/*',
    // __dirname + '/../rbhl/assets/js/rbhl/services/records/*',
    __dirname + '/../plugins/add_patient_step/static/js/add_patient_step/**/*.js',
  ];
  var includedFiles = [
    'opal/app.js',
    __dirname + '/../plugins/add_patient_step/static/js/add_patient_step/**/*.js',
    __dirname + '/../plugins/add_patient_step/static/js/test/*.js',
    // __dirname + '/../rbhl/assets/js/rbhl/**/*.js',
    // __dirname + '/../rbhl/assets/js/rbhltest/*.js',
  ];

  var defaultConfig = karmaDefaults(includedFiles, baseDir, coverageFiles);
  config.set(defaultConfig);
};
