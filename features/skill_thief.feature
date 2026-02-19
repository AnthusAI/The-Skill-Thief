Feature: Skill Thief CLI
  As a developer
  I want to install, update, and list Agent Skills from config
  So that my project stays synced with skill sources

  Background:
    Given a clean workspace
    And a config file with two skills

  Scenario: Install all skills
    When I run "skill-thief install"
    Then skill "alpha" should be installed
    And skill "beta" should be installed

  Scenario: Install a specific skill
    When I run "skill-thief install alpha"
    Then skill "alpha" should be installed
    And skill "beta" should not be installed

  Scenario: Update skills (same path as install)
    Given skill "alpha" is installed
    When I run "skill-thief update"
    Then skill "alpha" should be installed

  Scenario: List shows status
    Given skill "alpha" is installed
    When I run "skill-thief list"
    Then the output should contain "alpha"
    And the output should contain "beta"

  Scenario: Missing config shows error
    Given no config file exists
    When I run "skill-thief install"
    Then the command should fail

  Scenario: Invalid config schema shows error
    Given an invalid config file
    When I run "skill-thief install"
    Then the command should fail

  Scenario: Local source with subdir installs correctly
    When I run "skill-thief install beta"
    Then skill "beta" should be installed
    And SKILL.md for "beta" should have name "beta"

  Scenario: Git source with branch installs correctly
    Given a git repo source for "alpha"
    When I run "skill-thief install alpha"
    Then skill "alpha" should be installed

  Scenario: Validation warning when SKILL.md missing
    Given config skill "alpha" points to a source missing SKILL.md
    When I run "skill-thief install alpha"
    Then the output should contain "Missing SKILL.md"
