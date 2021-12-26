var app = angular.module('app', ['ngRoute', 'ngSanitize']);

app.config(['$routeProvider', function ($routeProvider) {
    $routeProvider.when('/', {
        templateUrl: './template/login.html',
        controller: 'loginController',
    })
        .otherwise({
            templateUrl: './404.html',
        });
}]);


app.controller("navbarController", function ($scope, $rootScope, $interval, $location) {
    $scope.links = [
        {"title": "Home", "link": "/"},
        {"title":"login", "link": "/login"},
        {"title":"logout", "link": "/logout"},
        {"title":"viewMeeting", "link": "/viewMeeting"},
    ]
    $rootScope.clickLink = function (link) {
        $location.path(link);
    }
})


app.controller("loginController", function ($scope, $rootScope, $interval, $location,$http) {
    $scope.usernameMan = ""
    $scope.passwordMan = ""
    $scope.pinMan = ""

    $scope.managerLogin = function () {
        var data = {
            "username": $scope.usernameMan,
            "password": $scope.passwordMan,
            "pin": $scope.pinMan
        }
        $http.post("http://localhost:8080/hello", JSON.stringify(data)).then(function (response) {
            console.log(response)
        })
    }
})