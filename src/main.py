import os
import supervisely_lib as sly
import pandas as pd



my_app = sly.AppService()
USER_ID = int(os.environ['context.userId'])
logger = sly.logger
project_type = 'images'


def check_classes(project_items):
    proj_classes = []
    for proj_item in project_items:
        proj_classes.append(proj_item['objectClass']['name'])
    return proj_classes


def check_tags(tags_stat):
    tags = []
    for tag_stat in tags_stat:
        tags.append(tag_stat['tagMeta']['name'])
    return tags


def check_object_tags_count(project_stat):
    tags_count = 0
    for tag_meta in project_stat['objectTags']['items']:
        tags_count += tag_meta['total']
    return tags_count


def check_image_tags_count(project_stat):
    tags_count = 0
    for tag_meta in project_stat['imageTags']['items']:
        tags_count += tag_meta['total']
    return tags_count


@my_app.callback("all_images_projects_summary")
@sly.timeit
def all_images_projects_summary(api: sly.Api, task_id, context, state, app_logger):

    columns = ['team', 'workspace', 'project', 'classes', 'tags', 'datasets', 'images', 'labels', 'image_tags', 'object_tags']
    data = []

    user_teams = api.user.get_teams(USER_ID)
    for user_team in user_teams:
        curr_team_name = user_team.name
        row = [curr_team_name]
        curr_team_id = user_team.id
        curr_team_workspaces = api.workspace.get_list(curr_team_id)
        row.append(len(curr_team_workspaces))
        projects_counter = 0
        classes_counter = []
        tags_counter = []
        datasets_counter = 0
        images_counter = 0
        labels_counter = 0
        image_tags_counter = 0
        object_tags_counter = 0
        for curr_workspace in curr_team_workspaces:
            curr_workspace_projects = api.project.get_list(curr_workspace.id)
            for project in curr_workspace_projects:
                if project.type != project_type:
                    continue
                projects_counter += 1
                project_stat = api.project.get_stats(project.id)
                classes_counter.extend(check_classes(project_stat['objects']['items']))
                tags_counter.extend(check_tags(project_stat['imageTags']['items']))
                datasets_counter += len(project_stat['datasets']['items'])
                images_counter += project_stat['images']['total']['imagesInDataset']
                labels_counter += project_stat['objects']['total']['objectsInDataset']
                image_tags_counter += check_image_tags_count(project_stat)
                object_tags_counter += check_object_tags_count(project_stat)
        row.extend([projects_counter, len(set(classes_counter)), len(set(tags_counter)), datasets_counter, images_counter, labels_counter, image_tags_counter, object_tags_counter])
        data.append(row)
    df = pd.DataFrame(data, columns=columns)
    print(df)

    my_app.stop()



def main():
    sly.logger.info("Script arguments", extra={
    })

    # Run application service
    my_app.run(initial_events=[{"command": "all_images_projects_summary"}])



if __name__ == '__main__':
        sly.main_wrapper("main", main)


