import tableauserverclient as TSC
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def main():
    # Step 1: Load Tableau Server details from environment variables
    tableau_server = os.getenv("TABLEAU_SERVER")
    tableau_username = os.getenv("TABLEAU_USERNAME")
    tableau_password = os.getenv("TABLEAU_PASSWORD")
    tableau_site = os.getenv("TABLEAU_SITE")
    view_name = input("Enter the name of the Tableau view to search for: ").strip()

    # Step 2: Tableau Server Authentication
    try:
        tableau_auth = TSC.TableauAuth(tableau_username, tableau_password)
        server = TSC.Server(tableau_server)
        server.use_server_version()
        print("Authenticating with Tableau Server...")

        with server.auth.sign_in(tableau_auth):
            print("Authentication successful!")

            # Step 3: Search for the view by name
            print(f"Searching for views with name containing '{view_name}'...")

            # Fetch all views
            all_views, pagination_item = server.views.get()
            matching_views = [
                view for view in all_views if view_name.lower() in view.name.lower()
            ]

            if matching_views:
                # Fetch all projects to match project names
                all_projects, _ = server.projects.get()

                print(f"Found {len(matching_views)} matching view(s):\n")
                for idx, view in enumerate(matching_views, start=1):
                    # Fetch related details about the workbook
                    workbook = server.workbooks.get_by_id(view.workbook_id)

                    # Match project name using the workbook's project ID
                    project_name = next(
                        (project.name for project in all_projects if project.id == workbook.project_id),
                        "Unknown Project"
                    )

                    # Construct the View URL
                    view_url = f"{tableau_server}/#/views/{view.content_url}"

                    print(f"{idx})")
                    print(f"- View Name: {view.name}")
                    print(f"- View ID: {view.id}")
                    print(f"- Workbook Name: {workbook.name}")
                    print(f"- Project Name: {project_name}")
                    print(f"- View URL: {view_url}")
                    print()
            else:
                print(f"No views found matching '{view_name}'.")

    except TSC.ServerResponseError as e:
        print(f"Server response error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()