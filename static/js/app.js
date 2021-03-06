var preContestApp = angular.module('preContestApp', ['ngRoute', 'preContestControllers']);
preContestApp.config(['$routeProvider',
    function($routeProvider) {
      $routeProvider
        .when('/home', {
            templateUrl: '/static/views/home.html',
            controller: 'HomeCtrl'
          })
        .when('/admin', {
          templateUrl: '/static/views/admin.html',
          controller: 'AdminCtrl'
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
          controller: 'ProblemCtrl',
          reloadOnSearch: false
        })
        .when('/scoreboard', {
          templateUrl: '/static/views/scoreboard.html',
          controller: 'ScoreboardCtrl'
        })
        .when('/submissions', {
          templateUrl: '/static/views/submissions.html',
          controller: 'SubmissionsCtrl'
        })
        .when('/admin', {
          templateUrl: '/static/views/admin.html',
          controller: 'AdminCtrl'
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

contestApp.directive('file', function(){
  return {
    scope: {
      file: '='
    },
    link: function(scope, el, attrs){
      el.bind('change', function(event){
        var files = event.target.files;
        var file = files[0];
        scope.file = file ? file.name : undefined;
        scope.$apply();
      });
    }
  };
});

contestApp.directive("fileread", [function () {
  return {
    scope: {
      fileread: "="
    },
    link: function (scope, element, attributes) {
      element.bind("change", function (changeEvent) {
        var reader = new FileReader();
        reader.onload = function (loadEvent) {
          scope.$apply(function () {
            scope.fileread = [ changeEvent.target.files[0].name,
                               loadEvent.target.result ];
          });
        }
        reader.readAsDataURL(changeEvent.target.files[0]);
      });
    }
  }
}]);

contestApp.filter('hasSomeResponse', [function(){
    return function(input, param) {
        var ret = [];
        if(!angular.isDefined(param)) param = true;
        angular.forEach(input, function(v, k){
            if(angular.isDefined(v.response)
               && v.response) {
                   v.response = v.response.replace(/^\s*/g, '');

                    v.position = k;
                    ret.push(v);
           }
        });
        return ret;
    };
}]);

contestApp.filter('hasNoResponse', [function(){
    return function(input, param) {
        var ret = [];
        if(!angular.isDefined(param)) param = true;
        angular.forEach(input, function(v, k){
            if(!angular.isDefined(v.response)
               || !v.response) {
                    v.position = k;
                    ret.push(v);
           }
        });
        return ret;
    };
}]);

