================
Grading
================

Overview
--------
The Grading system utilizes the the :doc:`api/Grade/grade_module` API to facilitate the grading process.

The general process is as follows:

#. Gradesheets are generated from the source document (:doc:`api/Grade/gradesheets`)
#. The gradesheet is selected by the Canvas module
#. The selected gradesheets move the ``Grade.grade`` where: (:doc:`api/Grade/grade`)
    #. Student scores are scaled
    #. Missing students are graded
    #. Extensions are processed
    #. Late Penalties are applied from the extensions
#. Then grades are converted to Canvas scores (:doc:`api/Grade/score`)
#. Finally, grades are posted to Canvas, and a backup Canvas gradebook is generated for manual posting (:doc:`api/Grade/post`)

The above serves as a useful overview for the general flow, but as you may imagine, there is a bit more to grading with this program,
like, for instance, coming up with the data.

There are 2 grading functions: ``Standard Grading`` and ``Post Pass Fail Assignment``. The below sections will explain how to use them.


Standard Grading
----------------


Post Pass Fail Assignment
-------------------------




