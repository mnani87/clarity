# Clarity One

## Introduction

**ClarityOne** is a project focussed on develioping small but useful apps. The goal is to have clear and simple apps, which do one thing well. 

***This is still a work-in-progress, but there are basic working prototypes of various apps available.***

These apps are presently designed for macOS. Though called v1, this is still very much a prototype; and the goal is to have polished versions releasing as v2 by the end of this year. 

There is no immediate plan to develop Linux- or Windows-compatible versions, but interested users can take a stab at this if they wish. 

A brief description of each app is as follows:

**Clarity Wiki** is a minimalist personal knowledge base and note-taking application designed to provide a seamless note management experience. Built on the philosophy of "do one thing well," it enables users to create and manage notes in markdown format while offering a live preview of the markdown content. The app supports a multi-wiki system, allowing users to categorize notes into different wikis for better organization. Users can easily format text using bold and italic shortcuts and navigate internal note links using double brackets (e.g., [[note]]). Clarity Wiki also includes a powerful tag management system, allowing users to filter and organize notes based on tags. Notes can be exported in HTML or PDF formats with customizable styles. Backlinks between notes are automatically detected and displayed, enabling users to track connections within their knowledge base. The app is designed with simplicity in mind, featuring a clean interface and easy-to-use toolbar for core note-taking actions like creating, editing, and searching notes.

**Clarity Explorer** is a file management system for Mac users that organizes files by project views, regardless of where the files are physically stored. It is designed to simplify file organization by allowing users to create multiple projects and associate files from different locations with each project. Users can manage their projects and add files without requiring the files to be moved, ensuring a non-intrusive and flexible organization method. The app offers tag-based file filtering, making it easy to categorize and find files. Users can also search for files within specific projects or across all projects simultaneously. Files are displayed in a list view, with the option to preview various file formats like text, PDFs, DOCX, and images within the app. Double-clicking a file opens it in the default application. Clarity Explorer supports adding, editing, and managing tags for files, and it also allows for missing file management by offering options to locate or remove missing files from the project. The user interface is clean and intuitive, featuring keyboard shortcuts for common actions. Designed for simplicity and efficiency, the app provides a powerful way to manage files organized by projects.

**Clarity Editor** is a distraction-free text editor for Mac, designed to provide a clean and efficient writing environment with essential formatting tools. It features a minimalist interface that allows users to focus on their writing without unnecessary distractions. The app includes basic formatting options like bold, italic, underline, alignment, bullet and numbered lists, and table insertion, all accessible through a simple toolbar. Users can easily change the font, font size, line spacing, and paragraph spacing to customize their writing experience. Clarity Editor supports saving documents in multiple formats, including HTML, Markdown, plain text, PDF, and ODT, ensuring compatibility with different workflows. The editor automatically tracks modifications, prompting users to save changes before closing or creating new documents. It also offers keyboard shortcuts for frequently used actions, improving efficiency. The app is built with ease of use in mind, catering to writers, students, and professionals who require a no-frills text editor with just enough formatting power to meet their needs. Its lightweight design and straightforward functionality make Clarity Editor an ideal tool for those who value simplicity in their writing process.

**Clarity Clips** is a distraction-free clipboard manager for Mac designed to help users organize and manage clipboard content efficiently. The app automatically records clipboard entries, allowing users to view, search, and manage past clipboard items. It includes functionality to add tags to specific entries, enabling easier categorization and retrieval of content. Users can copy previous entries back to the clipboard or delete items they no longer need. The app also supports exporting the clipboard history to a file for backup or external use. With a clean, intuitive interface, Clarity Clips helps users keep track of their clipboard without unnecessary complexity. The app runs in the background, accessible via the system tray, and provides keyboard shortcuts for quick access. It handles various content types, including text, HTML, PDFs, and Word documents, extracting plain text where possible. The app features a warning system when the clipboard history approaches a user-defined limit, ensuring that users can maintain control over their saved entries. Overall, Clarity Clips is designed to simplify clipboard management while maintaining a focus on clarity and ease of use.

**Clarity Calendar** is a minimalist, distraction-free calendar application for Mac users, designed to help manage daily events and tasks efficiently. The app features an intuitive interface, allowing users to add, edit, or delete events and tasks, with a focus on simplicity and usability. Events can include reminders, and tasks can be given deadlines and priority levels to ensure timely completion. The calendar widget highlights days with scheduled events, giving a clear overview of upcoming commitments. Clarity Calendar supports desktop notifications for reminders, ensuring users never miss important events. The app also includes import and export functionality, allowing users to back up or transfer their event and task data easily in JSON format. With the option to manage both tasks and events from separate tabs, Clarity Calendar provides users with an organized and clean experience. The app also incorporates keyboard shortcuts for quick actions, such as adding events or tasks, and a system tray feature that checks for reminders every minute. Overall, Clarity Calendar aims to provide a seamless experience for managing daily tasks and events while maintaining a simple, distraction-free environment.

**Clarity TimeKeeper** is a streamlined time tracking and management application for Mac users, designed to help individuals monitor and optimize their daily activities effectively. Embracing the ClarityOne philosophy of simplicity and functionality, TimeKeeper offers a clean interface that allows users to log activities effortlessly within a weekly grid layout. Users can assign specific activities to each two-hour-long block across seven days, providing a clear overview of how time is allocated throughout the week. The app highlights the current day, making it easy to focus on present and upcoming tasks. Customizable activity categories enable users to tailor the app to their unique workflows, while tagging and filtering options facilitate easy organization and retrieval of logged activities. TimeKeeper also features comprehensive reporting tools, allowing users to generate daily, weekly, or monthly summaries of their time usage. These reports include visual charts that help identify productivity patterns and areas for improvement. Data is automatically saved and reports can be generated in app. Data is all stored locally. Designed with both professionals and personal users in mind, Clarity TimeKeeper aims to enhance productivity by providing an intuitive and efficient way to manage time, without the complexity of overly feature-rich applications.

**Clarity Finances** is a financial management app designed for personal and small office finances. The app allows users to track expenses, receipts, and manage memos or invoices. Users can categorize expenses under default or custom categories such as "Professional Fees Paid," "Salaries," "Rent," and more. Clarity Finances automatically calculates totals for each financial year and allows users to filter and view monthly summaries. The app includes an export feature, enabling users to save their financial data in both JSON and CSV formats. With a simple and intuitive interface, Clarity Finances makes it easy to manage personal or office finances without unnecessary complexity. It is designed to help users stay organized, maintain clear financial records, and generate financial reports at the click of a button.


## Installation

Bundled .app versions are available to download for some of the apps: go to https://mnani87.github.io/mnanihome/clarityone.html

For building from source, you can clone the repository. Each app is contained in a single python script. There is a 'requirements' text file for each app. Use the 'clarityone_[appname].py' file if available, else use the 'clarity_[appname].py' scripts. Download requirements.txt for each app (or simply see the necessary imports at the start of the code for the app). Download the script and for easiest workflow, create a folder for each app. Place the downloaded script into the folder. Start a terminal session at the relevant folder. Start a virtual environment with `python3 -m venv venv` and then install dependencies as requirement with `pip install [dependencies]`. Then you can open the app with `python3 [scriptname.py]` - make sure to replace [dependencies] and ]scriptname.py] with the dependencies required to be installed, and with the actual name of the python file. Pyinstaller can be used to create your own .app version, which can be placed in your applications folders too. 

## Usage

Detailed user guides for each app are available: see https://mnani87.github.io/mnanihome/clarityone.html but for a brief overview, read on...

*Clarity Wiki*

Launch the App: Run the app by navigating to the clarity_wiki directory and executing the following:
        - python clarity_wiki.py

Creating and Managing Notes:
        - Create a new note by clicking the "New Note" button or using the keyboard shortcut Cmd+N.
        - Write in Markdown format, and the app will provide a live preview of the note in a split pane.
        - Use [[note]] syntax to link to other notes within your knowledge base.

Organizing Notes:
        - Assign tags to your notes to filter and categorize them easily.
        - Notes are organized by wikis, allowing you to maintain multiple knowledge bases.

Exporting Notes:
        -Export notes to HTML or PDF by clicking the "Export" button in the toolbar.

*Clarity Explorer*

Launching the App: Start Clarity Explorer by running:
        - python clarity_explorer.py

Adding Projects and Files:
        - Create a new project by clicking "New Project."
        - Add files from various locations to your projects by dragging them into the interface.
        - Files remain in their original location but are organized within your projects.

Tagging and Searching:
        - Use the tag management system to organize files within projects.
        - Search for files by project or across all projects using the search bar.

*Clarity Editor*

Opening the App: Run Clarity Editor with:
        - python clarity_editor.py

Writing and Formatting:
        - Focus on your writing in a distraction-free environment.
        - Use the toolbar or keyboard shortcuts (Cmd+B for bold, Cmd+I for italics, etc.) to format text.
        - Save documents in different formats such as HTML, Markdown, PDF, and plain text. 

Document Management:
        - Use Cmd+S to save your document.
        - Open existing documents by selecting the "Open" option in the file menu or using the shortcut Cmd+O.

*Clarity Clips*

Starting the App: Launch Clarity Clips by running:
    - python clarity_clip.py

Clipboard Management:
        - Clarity Clips automatically stores clipboard history. Every time you do a Cmd+C, Clip captures it and saves it.
        - Use the app to search, view, and tag clipboard entries.
        - Copy a past clipboard entry back to the clipboard by selecting it and clicking "Copy."

Exporting Clipboard History:
        - Export the entire clipboard history to a file for backup or future use by selecting the "Export" option.

*Clarity Calendar*

Launching the Calendar: Start the calendar by running:
        - python clarity_calendar.py

Managing Events and Tasks:
    - Use the toolbar to add events or tasks. Keyboard shortcuts are also available.
    - Set reminders for events and add priority levels for tasks.

View and Organize:
    - The calendar highlights dates with events, and tasks are organized by priority.
    - Check reminders with desktop notifications to ensure you stay on track.

*Clarity TimeKeeper*

Launching the Timekeeper: Start by running
        - python clarity_timekeeper.py

Logging Activities: Click on any time block within the weekly grid to assign an activity. Add custom activities as needed initially, and then choose from a dropdown. Use the "Clear" option to remove an activity from a time block.

Viewing Reports: Click the "View Reports" button to generate daily, weekly, or monthly reports. Reports include visual charts and can be exported in formats like HTML, PDF, and CSV for external analysis.

Clarity Finances

Launch the App: Run the app by navigating to the clarity_finances directory and executing the following:
        - python clarity_finances.py

Adding Memos: Add new memos or invoices using the "Add Memo" button. Enter memo details like memo number, date, client name, and amount.
    
Managing Receipts and Expenses: Track receipts and expenses, associating them with specific memos if necessary. Use "Add Receipt" or "Add Expense" to input new entries.

Viewing Summaries: View summaries of your financial data by selecting a specific financial year and month. The app automatically calculates totals for memos, receipts, and expenses.

Exporting Data: Export financial data in JSON or CSV format for backup or further analysis.

## Roadmap for future development 

Planned future enhancements for ClarityOne include:

*General Improvements:*
        - Add dark mode across all apps
        - Optimize performance with large datasets (e.g., large wikis, clipboard histories)
        - Provide better support for file recovery and missing file management 
        - Integrate the apps more (while ensuring users have the choice of whether to integrate or to use as standalone apps)

*Clarity Wiki:*
        - Integrate version history for notes
        - Implement a graph view to visualize connections between notes

*Clarity Explorer:*
        - Add support for drag-and-drop functionality
        - Implement batch tagging and editing of multiple files at once
        - Improve preview functionality

*Clarity Editor:*
        - Expand Markdown support to include tables, footnotes, and math formulas
        - Provide real-time collaboration features
        - Add support for .rtf, .docx

*Clarity Clips:*
        Add clipboard syncing across multiple devices
        Introduce an option for suggested auto-tagging based on content analysis

*Clarity Calendar:*
        - Implement recurring events and tasks
        - Provide support for syncing with other calendar services and exporting in compatible formats

*Clarity TimeKeeper:*
        - Integration with Calendar for a one-stop solution
        - Data export

*Clarity Finances:*
        - Adding support for tax calculations and return preparation
        - Support for reminders for forthcoming payments, advance tax payments etc.
        - Customised receipt and expense heads
        - Improvement of csv export functionality, to have files ready for import to Tally or other accounting software
        - Auto-generation of ledger entries and income & expenditure account

## Contributions for further development

We welcome contributions to ClarityOne! Here’s how you can help:

*Bug Reports:* If you encounter a bug, please open an issue on our GitHub repository, including detailed steps to reproduce the problem.

*Feature Requests:* If you have an idea for a new feature, feel free to submit it as a feature request. Please ensure that your suggestion aligns with the minimalist philosophy of ClarityOne.

*Code Contributions:* Fork the repository, create a new branch for your changes, and submit a pull request with a clear description of your contribution. Ensure your code adheres to the project's coding standards and is well-documented.

*Testing:* Help test the beta releases and provide feedback on performance, bugs, and usability.

## License

ClarityOne is licensed under the ***GNU General Public License v3.0***. You are free to use, modify, and redistribute the software under the terms of this license. The full license can be read here: https://www.gnu.org/licenses/gpl-3.0.html

