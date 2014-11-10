var preContestApp = angular.module('preContestApp', ['ngRoute', 'preContestControllers']);
preContestApp.config(['$routeProvider',
    function($routeProvider) {
      $routeProvider
        .when('/home', {
          templateUrl: '/static/views/home.html',
          controller: 'HomeCtrl'
        })
      .otherwise({
        redirectTo: '/home'
      });
    }]);

var contestApp = angular.module('contestApp', ['ngRoute', 'contestControllers', 'ui.bootstrap', 'ngCookies']);
contestApp.config(['$routeProvider',
    function($routeProvider) {
      $routeProvider
        .when('/home', {
          templateUrl: '/static/views/home.html',
          controller: 'HomeCtrl'
        })
      .when('/problems', {
        templateUrl: '/static/views/problems.html',
        controller: 'ProblemCtrl'
      })
      .when('/problems/:probId', {
        templateUrl: '/static/views/problems.html',
        controller: 'ProblemCtrl'
      })
      .when('/scoreboard', {
        templateUrl: '/static/views/scoreboard.html',
        controller: 'ScoreboardCtrl'
      })
      .otherwise({
        redirectTo: '/home'
      });
    }]);

contestApp.filter('unsafe', function($sce) {
  return function(val) {
    return $sce.trustAsHtml(val);
  };
});
