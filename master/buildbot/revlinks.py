# This file is part of Buildbot.  Buildbot is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright Buildbot Team Members

import re

class RevlinkMatch(object):
    def __init__(self, repo_urls, revlink):
        if isinstance(repo_urls, str) or isinstance(repo_urls, unicode):
            repo_urls = [ repo_urls ]
        self.repo_urls = map(re.compile, repo_urls)
        self.revlink = revlink
    def __call__(self, rev, repo):
        for url in self.repo_urls:
            m = url.match(repo)
            if m:
                return m.expand(self.revlink) % rev

GithubRevlink = RevlinkMatch(
        repo_urls = [ r'https://github.com/([^/]*)/([^/]*?)(?:\.git)?$',
            r'git://github.com/([^/]*)/([^/]*?)(?:\.git)?$',
            r'git@github.com:([^/]*)/([^/]*?)(?:\.git)?$',
            r'ssh://git@github.com/([^/]*)/([^/]*?)(?:\.git)?$'
            ],
        revlink = r'https://github.com/\1/\2/commit/%s')

class GitwebMatch(RevlinkMatch):
    def __init__(self, repo_urls, revlink):
        RevlinkMatch.__init__(self, repo_urls = repo_urls, revlink = revlink + r'?p=\g<repo>;a=commit;h=%s')

SourceforgeGitRevlink = GitwebMatch(
        repo_urls = [ r'^git://([^.]*).git.sourceforge.net/gitroot/(?P<repo>.*)$',
            r'[^@]*@([^.]*).git.sourceforge.net:gitroot/(?P<repo>.*)$',
            r'ssh://(?:[^@]*@)?([^.]*).git.sourceforge.net/gitroot/(?P<repo>.*)$',
            ],
        revlink = r'http://\1.git.sourceforge.net/git/gitweb.cgi')

class RevlinkMultiplexer(object):
    def __init__(self, *revlinks):
        self.revlinks = revlinks
    def __call__(self, rev, repo):
        for revlink in self.revlinks:
            url = revlink(rev, repo)
            if url:
                return url

default_revlink_matcher = RevlinkMultiplexer(GithubRevlink, SourceforgeGitRevlink)
