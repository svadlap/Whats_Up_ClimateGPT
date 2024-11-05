# GMU_DAEN_Team_1 - What’s Up ClimateGPT

# Repository Overview

This repository is part of the DAEN 690 Capstone Project at the College of Engineering, Fall 2024. The project focuses on improving the performance of ClimateGPT, an open-source AI model developed by Erasmus.AI in collaboration with the Club of Rome Climate. ClimateGPT is designed to assist researchers, policymakers, and business leaders in making informed decisions about climate change mitigation and adaptation. Here are the key features and goals that will be addressed by the end of this project.

# Key Features

<ul> <li><strong>AI Classifier Development:</strong> A sophisticated AI classifier to accurately parse user queries and determine whether they should be handled by ClimateGPT’s core model or require querying external climate databases.
  
</li> <li><strong>Structured Query Framework:</strong> A robust framework for querying multiple climate-related databases (NOAA, NASA, IPCC, etc.) using structured SQL queries through APIs, combined with advanced function calls to streamline data retrieval based on user queries.
  
</li> <li><strong>Multi-Modal Response Generation:</strong> ClimateGPT supports rich, multi-modal outputs, including text, data visualizations, and references tailored for complex climate scenarios. The enhanced functionality includes the integration of function calls to generate precise and varied responses based on the user's specific input.
  
</li> <li><strong>Open-Source and Scalable:</strong> Built on open-source technologies with scalability in mind, ensuring that the model can be continuously improved and scaled to handle larger datasets and more complex queries.</li> </ul>

# Goals

<ul> <li><strong>Improve Query Classification:</strong> Enhance the AI’s ability to distinguish between queries that can be handled internally by ClimateGPT’s model and those that require external data. Function calls will allow the model to trigger nested functions for more specialized datasets as necessary.

</li> <li><strong>Integrate External Databases:</strong> Connect and query key climate databases for comprehensive, data-driven insights using pre-built prompts and function calls.

</li> <li><strong>Optimize Response Formats:</strong> Develop effective prompt engineering strategies that leverage function calls to generate user-friendly, contextually rich outputs.

</li> <li><strong>Enable Rich, Multi-Modal Outputs:</strong> Provide detailed and contextually relevant responses across different media formats, such as graphs, charts, and tables, using both the core ClimateGPT model and function-based outputs.</li> </ul>

# Code Files and Databases

The code files in this repository follow the naming conventions below to maintain clarity and consistency:<br>

<ul> <li><strong>Function_Name_tool.ipynb:</strong> Contains the function implementations developed for selected datasets. Each file represents a tool tailored for a specific dataset.</li>
  
<li><strong>custom_tools.ipynb:</strong> This file is part of the Meta's Llama Stack repository, and it contains the base classes that developers can use to define their custom tools. Any custom tool that needs to integrate with the Llama agent must extend this class.</li>

<li><strong>e2e_loop_with_custom_tools.ipynb:</strong> Integrates the <code>Function_Name_tool.ipynb</code> files with the large language model (LLM), specifically the Llama 3.1 model, and serves as the unit testing environment for the developed function calls and for end-to-end testing, simulating real-world query handling with custom tools.</li> 

<li><strong>Function Name Tool Guide.pdf:</strong> The document titled "Function Name Tool Guide.pdf" likely provides a comprehensive guide on how to use a specific function tool, including its setup, functionality, and how it integrates with the larger project. It probably explains the steps to install, configure, and execute the tool, the types of data or queries it handles, and the expected outcomes when the tool is run. Additionally, it may cover any necessary pre-processing, error handling, and how to interact with the tool using an interface or API, likely within the context of a broader system like ClimateGPT. </ul></li>
