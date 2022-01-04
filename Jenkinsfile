pipeline {
    agent {
        node {
            label 'master'
        }
    }

    stages {
        stage('clean') {
            steps {
                bat '"%GIT_PATH%"\\git.exe clean -fdx'
                bat '"%GIT_PATH%"\\git.exe reset --hard'
            }
        }

        stage('requestIARLicense') {
            steps {
                bat '"%PYTHON_PATH%"\\python.exe .\\scripts\\automation\\request_iar_license.py'
            }
        }

        stage('build') {
            steps {
                bat '%PYTHON_PATH%\\python.exe .\\scripts\\automation\\build.py'
            }
        }
        stage('releaseIARLicense') {
            steps {
                bat '"%PYTHON_PATH%"\\python.exe .\\scripts\\automation\\release_iar_license.py'
            }
        }
    }

    post {
        success {
            bat 'if not exist I: (net use I: \\\\cn-s-031fil1.cn.abb.com\\sha1data$)'
            bat '%PYTHON_PATH%\\python.exe .\\scripts\\automation\\store_image.py'

            emailext attachmentsPattern: 'scripts\\automation\\tmp\\build_log.txt',
            body: env.JOB_NAME + "/" + env.GIT_BRANCH + " - Build # " + env.BUILD_NUMBER + " - Success:\n\nCheck console output at " + env.BUILD_URL +
            " to view the results.\n\nYou can find the build result from " + env.IMAGE_STORAGE_PATH + "\\" + env.JOB_NAME.replace("/", "\\"),
            subject: env.JOB_NAME + " - Build # " + env.BUILD_NUMBER + " - Success!",
            // to: 'gongyan.chen@cn.abb.com, haiqing.zhao@cn.abb.com, jaden-jinding.liu@cn.abb.com, jimmy-ge.wang@cn.abb.com, panpan.zhang@cn.abb.com'
            to: 'panpan.zhang@cn.abb.com'
        }

        failure {
            emailext attachmentsPattern: 'scripts\\automation\\tmp\\build_log.txt',
            body: env.JOB_NAME + "/" + env.GIT_BRANCH + " - Build # " + env.BUILD_NUMBER + " - Failed:\n\nCheck console output at " + env.BUILD_URL + " to view the results.",
            subject: env.JOB_NAME + " - Build # " + env.BUILD_NUMBER + " - Failed!",
            // to: 'gongyan.chen@cn.abb.com, haiqing.zhao@cn.abb.com, jaden-jinding.liu@cn.abb.com, jimmy-ge.wang@cn.abb.com, panpan.zhang@cn.abb.com'
            to: 'panpan.zhang@cn.abb.com'
        }
    }
}
