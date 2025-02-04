import tableauserverclient as TSC
import urllib.parse
import os
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()

    # Tableau Server credentials
    tableau_server = os.getenv("TABLEAU_SERVER")
    tableau_username = os.getenv("TABLEAU_USERNAME")
    tableau_password = os.getenv("TABLEAU_PASSWORD")
    tableau_site = os.getenv("TABLEAU_SITE")  # Use None for the default site

    if not all([tableau_server, tableau_username, tableau_password]):
        print("Error: Missing Tableau credentials. Check your .env file.")
        return

    # Prompt user for view URL
    user_input = input("Enter the URL of the Tableau view to search for: ").strip()

    # Parse and extract view information from the URL
    parsed_url = urllib.parse.urlparse(user_input)
    view_path = parsed_url.path.split("/")[-1] if "/" in parsed_url.path else user_input

    # Authenticate with Tableau Server
    tableau_auth = TSC.TableauAuth(tableau_username, tableau_password)
    server = TSC.Server(tableau_server)
    server.use_server_version()

    try:
        with server.auth.sign_in(tableau_auth):
            # Search for the view
            req_options = TSC.RequestOptions()
            req_options.filter.add(
                TSC.Filter(
                    TSC.RequestOptions.Field.Name,
                    TSC.RequestOptions.Operator.Equals,
                    view_path,
                )
            )

            views, pagination_item = server.views.get(req_options)

            if views:
                print("\nFound the following view(s):\n")
                for idx, view in enumerate(views, start=1):
                    # Get workbook details
                    workbook = server.workbooks.get_by_id(view.workbook_id)
                    
                    # Get project details
                    all_projects, _ = server.projects.get()
                    project = next((proj for proj in all_projects if proj.id == workbook.project_id), None)

                    print(f"{idx})")
                    print(f"- View Name: {view.name}")
                    print(f"- View ID: {view.id}")
                    print(f"- Workbook Name: {workbook.name}")
                    print(f"- Project Name: {project.name if project else 'Unknown'}")
                    print(f"- View URL: {tableau_server}/views/{workbook.name}/{view.name}\n")
            else:
                print("\nNo views found matching the given URL.\n")

    except TSC.ServerResponseError as e:
        print(f"An error occurred while communicating with Tableau Server: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
