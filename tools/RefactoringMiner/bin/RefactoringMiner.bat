@rem
@rem Copyright 2015 the original author or authors.
@rem
@rem Licensed under the Apache License, Version 2.0 (the "License");
@rem you may not use this file except in compliance with the License.
@rem You may obtain a copy of the License at
@rem
@rem      https://www.apache.org/licenses/LICENSE-2.0
@rem
@rem Unless required by applicable law or agreed to in writing, software
@rem distributed under the License is distributed on an "AS IS" BASIS,
@rem WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
@rem See the License for the specific language governing permissions and
@rem limitations under the License.
@rem
@rem SPDX-License-Identifier: Apache-2.0
@rem

@if "%DEBUG%"=="" @echo off
@rem ##########################################################################
@rem
@rem  RefactoringMiner startup script for Windows
@rem
@rem ##########################################################################

@rem Set local scope for the variables with windows NT shell
if "%OS%"=="Windows_NT" setlocal

set DIRNAME=%~dp0
if "%DIRNAME%"=="" set DIRNAME=.
@rem This is normally unused
set APP_BASE_NAME=%~n0
set APP_HOME=%DIRNAME%..

@rem Resolve any "." and ".." in APP_HOME to make it shorter.
for %%i in ("%APP_HOME%") do set APP_HOME=%%~fi

@rem Add default JVM options here. You can also use JAVA_OPTS and REFACTORING_MINER_OPTS to pass JVM options to this script.
set DEFAULT_JVM_OPTS=

@rem Find java.exe
if defined JAVA_HOME goto findJavaFromJavaHome

set JAVA_EXE=java.exe
%JAVA_EXE% -version >NUL 2>&1
if %ERRORLEVEL% equ 0 goto execute

echo. 1>&2
echo ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH. 1>&2
echo. 1>&2
echo Please set the JAVA_HOME variable in your environment to match the 1>&2
echo location of your Java installation. 1>&2

goto fail

:findJavaFromJavaHome
set JAVA_HOME=%JAVA_HOME:"=%
set JAVA_EXE=%JAVA_HOME%/bin/java.exe

if exist "%JAVA_EXE%" goto execute

echo. 1>&2
echo ERROR: JAVA_HOME is set to an invalid directory: %JAVA_HOME% 1>&2
echo. 1>&2
echo Please set the JAVA_HOME variable in your environment to match the 1>&2
echo location of your Java installation. 1>&2

goto fail

:execute
@rem Setup the command line

set CLASSPATH=%APP_HOME%\lib\RefactoringMiner-3.1.3.jar;%APP_HOME%\lib\swc4j-2.1.0.jar;%APP_HOME%\lib\swc4j-macos-arm64-2.1.0.jar;%APP_HOME%\lib\swc4j-linux-x86_64-2.1.0.jar;%APP_HOME%\lib\antlr4-runtime-4.13.2.jar;%APP_HOME%\lib\kotlin-compiler-embeddable-2.3.20.jar;%APP_HOME%\lib\org.eclipse.jgit-6.10.1.202505221210-r.jar;%APP_HOME%\lib\spark-core-2.9.4.jar;%APP_HOME%\lib\logback-classic-1.5.32.jar;%APP_HOME%\lib\slf4j-api-2.0.17.jar;%APP_HOME%\lib\gen.jdt-3.0.0.jar;%APP_HOME%\lib\org.eclipse.jdt.core-3.45.0.jar;%APP_HOME%\lib\commons-text-1.15.0.jar;%APP_HOME%\lib\github-api-1.330.jar;%APP_HOME%\lib\java-diff-utils-4.16.jar;%APP_HOME%\lib\core-3.0.0.jar;%APP_HOME%\lib\gen.treesitter-ng-4.0.0-beta6.jar;%APP_HOME%\lib\jcommander-3.0.jar;%APP_HOME%\lib\jsoup-1.22.1.jar;%APP_HOME%\lib\p4java-2025.2.2872146.jar;%APP_HOME%\lib\fastutil-8.5.18.jar;%APP_HOME%\lib\rendersnake-1.9.0.jar;%APP_HOME%\lib\kotlin-stdlib-2.3.20.jar;%APP_HOME%\lib\kotlin-script-runtime-2.3.20.jar;%APP_HOME%\lib\kotlin-reflect-1.6.10.jar;%APP_HOME%\lib\kotlin-daemon-embeddable-2.3.20.jar;%APP_HOME%\lib\kotlinx-coroutines-core-jvm-1.8.0.jar;%APP_HOME%\lib\JavaEWAH-1.2.3.jar;%APP_HOME%\lib\simmetrics-core-3.2.3.jar;%APP_HOME%\lib\commons-codec-1.17.0.jar;%APP_HOME%\lib\org.eclipse.core.resources-3.23.200.jar;%APP_HOME%\lib\org.eclipse.core.filesystem-1.11.400.jar;%APP_HOME%\lib\org.eclipse.text-3.14.600.jar;%APP_HOME%\lib\org.eclipse.core.expressions-3.9.500.jar;%APP_HOME%\lib\org.eclipse.core.runtime-3.34.200.jar;%APP_HOME%\lib\ecj-3.45.0.jar;%APP_HOME%\lib\commons-lang3-3.20.0.jar;%APP_HOME%\lib\jackson-core-2.20.0.jar;%APP_HOME%\lib\jackson-databind-2.20.0.jar;%APP_HOME%\lib\commons-io-2.17.0.jar;%APP_HOME%\lib\classindex-3.13.jar;%APP_HOME%\lib\gson-2.8.2.jar;%APP_HOME%\lib\jgrapht-core-1.5.1.jar;%APP_HOME%\lib\snakeyaml-2.0.jar;%APP_HOME%\lib\tree-sitter-c-0.23.2.jar;%APP_HOME%\lib\tree-sitter-cpp-0.23.4.jar;%APP_HOME%\lib\tree-sitter-cmake-0.4.1a.jar;%APP_HOME%\lib\tree-sitter-c-sharp-0.23.1.jar;%APP_HOME%\lib\tree-sitter-go-0.23.3.jar;%APP_HOME%\lib\tree-sitter-javascript-0.23.1.jar;%APP_HOME%\lib\tree-sitter-kotlin-0.3.8.1.jar;%APP_HOME%\lib\tree-sitter-java-0.23.4.jar;%APP_HOME%\lib\tree-sitter-ocaml-0.23.2.jar;%APP_HOME%\lib\tree-sitter-php-0.23.11.jar;%APP_HOME%\lib\tree-sitter-python-0.23.4.jar;%APP_HOME%\lib\tree-sitter-r-main-a.jar;%APP_HOME%\lib\tree-sitter-ruby-0.23.1.jar;%APP_HOME%\lib\tree-sitter-rust-0.23.1.jar;%APP_HOME%\lib\tree-sitter-swift-0.5.0.jar;%APP_HOME%\lib\tree-sitter-typescript-0.23.2.jar;%APP_HOME%\lib\tree-sitter-0.25.3.jar;%APP_HOME%\lib\jzlib-1.1.3.jar;%APP_HOME%\lib\jsr305-3.0.2.jar;%APP_HOME%\lib\jetty-webapp-9.4.48.v20220622.jar;%APP_HOME%\lib\websocket-server-9.4.48.v20220622.jar;%APP_HOME%\lib\jetty-servlet-9.4.48.v20220622.jar;%APP_HOME%\lib\jetty-security-9.4.48.v20220622.jar;%APP_HOME%\lib\jetty-server-9.4.48.v20220622.jar;%APP_HOME%\lib\websocket-servlet-9.4.48.v20220622.jar;%APP_HOME%\lib\junit-4.8.2.jar;%APP_HOME%\lib\spring-webmvc-4.1.6.RELEASE.jar;%APP_HOME%\lib\jtidy-r938.jar;%APP_HOME%\lib\guice-3.0.jar;%APP_HOME%\lib\javax.inject-1.jar;%APP_HOME%\lib\logback-core-1.5.32.jar;%APP_HOME%\lib\annotations-13.0.jar;%APP_HOME%\lib\jna-platform-5.18.1.jar;%APP_HOME%\lib\jna-5.18.1.jar;%APP_HOME%\lib\org.eclipse.core.jobs-3.15.700.jar;%APP_HOME%\lib\org.eclipse.core.contenttype-3.9.800.jar;%APP_HOME%\lib\org.eclipse.equinox.app-1.7.600.jar;%APP_HOME%\lib\org.eclipse.equinox.registry-3.12.600.jar;%APP_HOME%\lib\org.eclipse.equinox.preferences-3.12.100.jar;%APP_HOME%\lib\org.eclipse.core.commands-3.12.500.jar;%APP_HOME%\lib\org.eclipse.equinox.common-3.20.300.jar;%APP_HOME%\lib\org.eclipse.osgi-3.24.100.jar;%APP_HOME%\lib\jackson-annotations-2.20.jar;%APP_HOME%\lib\guava-18.0.jar;%APP_HOME%\lib\jheaps-0.13.jar;%APP_HOME%\lib\javax.servlet-api-3.1.0.jar;%APP_HOME%\lib\websocket-client-9.4.48.v20220622.jar;%APP_HOME%\lib\jetty-client-9.4.48.v20220622.jar;%APP_HOME%\lib\jetty-http-9.4.48.v20220622.jar;%APP_HOME%\lib\websocket-common-9.4.48.v20220622.jar;%APP_HOME%\lib\jetty-io-9.4.48.v20220622.jar;%APP_HOME%\lib\jetty-xml-9.4.48.v20220622.jar;%APP_HOME%\lib\websocket-api-9.4.48.v20220622.jar;%APP_HOME%\lib\spring-web-4.1.6.RELEASE.jar;%APP_HOME%\lib\spring-context-4.1.6.RELEASE.jar;%APP_HOME%\lib\spring-aop-4.1.6.RELEASE.jar;%APP_HOME%\lib\spring-beans-4.1.6.RELEASE.jar;%APP_HOME%\lib\spring-expression-4.1.6.RELEASE.jar;%APP_HOME%\lib\spring-core-4.1.6.RELEASE.jar;%APP_HOME%\lib\aopalliance-1.0.jar;%APP_HOME%\lib\cglib-2.2.1-v20090111.jar;%APP_HOME%\lib\org.osgi.service.prefs-1.1.2.jar;%APP_HOME%\lib\jetty-util-ajax-9.4.48.v20220622.jar;%APP_HOME%\lib\jetty-util-9.4.48.v20220622.jar;%APP_HOME%\lib\commons-logging-1.2.jar;%APP_HOME%\lib\asm-3.1.jar;%APP_HOME%\lib\osgi.annotation-8.0.1.jar


@rem Execute RefactoringMiner
"%JAVA_EXE%" %DEFAULT_JVM_OPTS% %JAVA_OPTS% %REFACTORING_MINER_OPTS%  -classpath "%CLASSPATH%" org.refactoringminer.RefactoringMiner %*

:end
@rem End local scope for the variables with windows NT shell
if %ERRORLEVEL% equ 0 goto mainEnd

:fail
rem Set variable REFACTORING_MINER_EXIT_CONSOLE if you need the _script_ return code instead of
rem the _cmd.exe /c_ return code!
set EXIT_CODE=%ERRORLEVEL%
if %EXIT_CODE% equ 0 set EXIT_CODE=1
if not ""=="%REFACTORING_MINER_EXIT_CONSOLE%" exit %EXIT_CODE%
exit /b %EXIT_CODE%

:mainEnd
if "%OS%"=="Windows_NT" endlocal

:omega
