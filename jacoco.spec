%{?_javapackages_macros:%_javapackages_macros}
%global tag 201306030806

Name:      jacoco
Version:   0.6.3
Release:   5.0%{?dist}
Summary:   Java Code Coverage for Eclipse 

License:   EPL
URL:       http://www.eclemma.org/jacoco/
Source0:   https://github.com/jacoco/jacoco/archive/v%{version}.tar.gz

Patch0:    removeGroovyScripting.patch

BuildArch:        noarch

BuildRequires:    java-devel
BuildRequires:    jpackage-utils
BuildRequires:    eclipse-platform >= 1:4.2.0-0.10
BuildRequires:    eclipse-pde >= 1:4.2.0-0.10
BuildRequires:    tycho
BuildRequires:    maven-shade-plugin >= 1.5
BuildRequires:    maven-enforcer-plugin
BuildRequires:    maven-dependency-plugin maven-antrun-plugin maven-assembly-plugin maven-clean-plugin maven-compiler-plugin maven-deploy-plugin
BuildRequires:    maven-install-plugin maven-invoker-plugin maven-gpg-plugin maven-jar-plugin maven-javadoc-plugin maven-plugin-plugin
BuildRequires:    maven-release-plugin maven-resources-plugin maven-shade-plugin maven-source-plugin maven-surefire-plugin maven-site-plugin
BuildRequires:    maven-plugin-tools-javadoc
BuildRequires:	  maven-plugin-build-helper
BuildRequires:    dos2unix
%if 0%{?fedora}
BuildRequires:    fest-assert
%endif
BuildRequires:    objectweb-asm4
Requires:         java >= 1.7
Requires:         ant
Requires:         objectweb-asm4

%description
JaCoCo is a free code coverage library for Java, 
which has been created by the EclEmma team based on the lessons learned 
from using and integration existing libraries over the last five years. 


%package    javadoc
Summary:    Java-docs for %{name}

Requires:   %{name} = %{version}-%{release}
Requires:   jpackage-utils

%description javadoc
This package contains the API documentation for %{name}.

%package    maven-plugin
Summary:    A Jacoco plugin for maven

Requires:   java
Requires:   maven
Requires:   objectweb-asm4
Requires:   %{name} = %{version}-%{release}

%description maven-plugin
A Jacoco plugin for maven.

%prep
%setup -q 
%patch0

%pom_disable_module ../org.jacoco.examples org.jacoco.build
%pom_disable_module ../org.jacoco.doc org.jacoco.build
%pom_disable_module ../org.jacoco.tests org.jacoco.build
%pom_disable_module ../jacoco org.jacoco.build

#%pom_remove_plugin org.apache.maven.plugins:maven-shade-plugin org.jacoco.agent.rt/pom.xml 

# make sure upstream hasn't sneaked in any jars we don't know about
JARS=""
for j in `find -name "*.jar"`; do
  if [ ! -L $j ]; then
    JARS="$JARS $j"
  fi
done
if [ ! -z "$JARS" ]; then
   echo "These jars should be deleted and symlinked to system jars: $JARS"
   exit 1
fi

%build
# Note: Tests must be disabled because they introduce circular dependency
# right now.
OPTIONS="-DrandomNumber=${RANDOM} -DskipTychoVersionCheck package javadoc:aggregate" 

mvn-rpmbuild $OPTIONS

dos2unix org.jacoco.doc/docroot/doc/.resources/doc.css 

%install
install -d -m 755 %{buildroot}%{_javadir}/%{name}

for f in    org.jacoco.agent \
            org.jacoco.ant \
            org.jacoco.core \
            org.jacoco.report
do
    cp $f/target/$f-%{version}.%{tag}.jar %{buildroot}%{_javadir}/%{name}/$f.jar
done;

cp org.jacoco.agent.rt/target/org.jacoco.agent.rt-%{version}.%{tag}-all.jar %{buildroot}%{_javadir}/%{name}/org.jacoco.agent.rt.jar

# Install maven stuff.
install -d -m 755 %{buildroot}%{_mavenpomdir}
install -pm 644 org.jacoco.build/pom.xml %{buildroot}/%{_mavenpomdir}/JPP-%{name}.pom
%add_maven_depmap JPP-%{name}.pom

for f in    org.jacoco.agent \
            org.jacoco.agent.rt \
            org.jacoco.ant \
            org.jacoco.core \
            org.jacoco.report
do
    install -pm 644 $f/pom.xml %{buildroot}/%{_mavenpomdir}/JPP.%{name}-$f.pom
    %add_maven_depmap JPP.%{name}-$f.pom %{name}/$f.jar
done;

# maven plugin
cp jacoco-maven-plugin/target/jacoco-maven-plugin-%{version}.%{tag}.jar %{buildroot}%{_javadir}/jacoco-maven-plugin.jar
install -pm 644 jacoco-maven-plugin/pom.xml %{buildroot}/%{_mavenpomdir}/JPP-jacoco-maven-plugin.pom
%add_maven_depmap JPP-jacoco-maven-plugin.pom jacoco-maven-plugin.jar -f plugin

# javadoc 
install -d -m 755 %{buildroot}%{_javadocdir}/%{name}
cp -rf target/site/* %{buildroot}%{_javadocdir}/%{name}

%files
%{_mavendepmapfragdir}/%{name}
%{_mavenpomdir}/JPP-%{name}.pom
#agent
%{_javadir}/jacoco/org.jacoco.agent.rt.jar
%{_mavenpomdir}/JPP.%{name}-org.jacoco.agent.rt.pom
#OSGi bundles
%{_javadir}/jacoco/org.jacoco.ant.jar
%{_javadir}/jacoco/org.jacoco.agent.jar
%{_javadir}/jacoco/org.jacoco.core.jar
%{_javadir}/jacoco/org.jacoco.report.jar
%{_mavenpomdir}/JPP.%{name}-org.jacoco.ant.pom
%{_mavenpomdir}/JPP.%{name}-org.jacoco.agent.pom
%{_mavenpomdir}/JPP.%{name}-org.jacoco.core.pom
%{_mavenpomdir}/JPP.%{name}-org.jacoco.report.pom

%doc org.jacoco.doc/docroot/*
%doc org.jacoco.doc/about.html

%files maven-plugin
%{_mavendepmapfragdir}/%{name}-plugin
%{_javadir}/jacoco-maven-plugin.jar
%{_mavenpomdir}/JPP-jacoco-maven-plugin.pom

%files javadoc
%{_javadocdir}/%{name}/

%changelog
* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6.3-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Jul 22 2013 Krzysztof Daniel <kdaniel@redhat.com> 0.6.3-4
- Move maven plugin to the %%{javadir}.

* Mon Jul 22 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 0.6.3-3
- Move plugin artifact to plugin subpackage
- Resolves: rhbz#987084

* Thu Jun 20 2013 Krzysztof Daniel <kdaniel@redhat.com> 0.6.3-2
- Add missing BR.

* Thu Jun 20 2013 Krzysztof Daniel <kdaniel@redhat.com> 0.6.3-1
- Update to 0.6.3.

* Wed May 8 2013 Krzysztof Daniel <kdaniel@redhat.com> 0.6.2-1
- Update to latest upstream.

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Mon Dec 10 2012 Krzysztof Daniel <kdaniel@redhat.com> 0.6.0-3
- Merge the master branch in.

* Thu Nov 29 2012 Krzysztof Daniel <kdaniel@redhat.com> 0.6.0-2
- Package correct agent.
- Improve the name of packages.

* Wed Nov 21 2012 Alexander Kurtakov <akurtako@redhat.com> 0.6.0-1
- Update to upstream 0.6.0.

* Mon Sep 17 2012 Krzysztof Daniel <kdaniel@redhat.com> 0.5.9-2
- Add BR to fest-assert.

* Tue Sep 11 2012 Krzysztof Daniel <kdaniel@redhat.com> 0.5.9-1
- Update to upstream 0.5.10 release.

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5.7-0.6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue May 8 2012 Krzysztof Daniel <kdaniel@redhat.com> 0.5.7-0.5
- Dropped dependency version to maven-shade-plugin.

* Tue May 8 2012 Krzysztof Daniel <kdaniel@redhat.com> 0.5.7-0.4
- Fixed rpmlint warnings.

* Tue May 8 2012 Krzysztof Daniel <kdaniel@redhat.com> 0.5.7-0.3
- Removed symlink to java.

* Tue May 8 2012 Krzysztof Daniel <kdaniel@redhat.com> 0.5.7-0.2
- Restructured packages
- Generated javadoc as set of plain files.

* Thu May 3 2012 Krzysztof Daniel <kdaniel@redhat.com> 0.5.7-0.1
- Initial release.
