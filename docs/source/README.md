# Grade Posting Script
> A program designed to accelerate the grade posting process from Gradescope to Canvas

?> This documentation is a work in progress
## Overview

### Why? <!-- {docsify-ignore} -->

It is important to recognise the reasons behind creating this script as it will explain a lot of the choices that I made.

This script was built primarily due to the ridiculous amounts of time that went into posting grades and the workflow
inefficiencies that contributed to long times between grading being completed and grades being made available 
to students. From a student perceptive this delay was unacceptable, as students would be waiting as much as four weeks 
after they submitted their work. From a TA perceptive: the amount of work that would go into applying special cases, 
removing late penalties if they are incorrectly applied by an autograder, and then recalculating late penalties after
making the appropriate adjustments to late passes, would take _far_ too long and be prone to errors or 
miscalculations not to mention the issues with the existing script for publishing scores to canvas. 

So with the permission of the powers that be, I set out to develop an all encompassing script 
to accelerate the grading process and reduce the workload and sources of errors for our TAs. 

### What? <!-- {docsify-ignore} -->

This script allows grades to be loaded in from Gradescope (or equivalent CSV file formats) and have all extensions and 
penalties applied automatically. It then posts the scores directly to Canvas with a comment explaining to the student 
where points were lost (due to lateness or otherwise) as well as any extensions the student may have received. 

This script will also update all status assignments defined in the config file then post them to Canvas as well. 

!> Due to current limitations with the way that status assignments are implemented, only one should be used per course.

### How? <!-- {docsify-ignore} -->

I'll get into more specific steps in [Getting Started](getting_started.md), but the general steps to start using this 
program are:
1. Generate a Canvas API key
2. Get your user ID from canvas 
3. Download the compiled program from [here]() for your platform of choice 
4. Create the required folder structure
5. Finally, run the script for the first time to create a config file

!> Do **not** use the script for classes that you are not an authorized grader for. It is _very_ easy to audit misuse of this script.

As far as actually grading, I will go into more specific detail in [Grading](grading.md), but the general process is:
1. Download grades as a CSV from Gradescope for _all_ assignments you will be grading
2. Create a working copy of the current special cases spreadsheet, verifying that all duplicates are resolved
3. Run the script in `Standard Grading` mode
4. Follow the prompts to post grades to Canvas
5. Merge the updated special cases sheet with the master sheet
6. Verify that the grades posted to Canvas are what you think they are
7. Publish grades to students from Canvas

!> Always verify that what you posted aligns with what should be posted to Canvas. It will save hundreds of emails later to both you and the lovely course instructors.

## Making Changes

I welcome changes and suggestions. However, I ask that you create an issue on GitHub with either the Feature Request 
template or the Bug Report template.

[//]: # (?> If you do not have access to the GitHub, reach out to me on Slack. )

Please create your proposed revision in a feature branch and create a pull request when you are ready. Please add me as 
a code reviewer and do not be discouraged if I ask you to make changes. It's all part of the process. 
If you have any questions about the code base or about how to approach an issue, please, please, please ask questions.

I go into more detail on the design and architecture of this program [here]().
