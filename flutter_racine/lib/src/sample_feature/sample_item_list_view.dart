import 'package:flutter/material.dart';

import '../settings/settings_view.dart';
import 'sample_item.dart';
import 'sample_item_details_view.dart';

import 'package:requests/requests.dart';
import 'package:html/parser.dart';

/// Displays a list of SampleItems.
class SampleItemListView extends StatefulWidget {
  const SampleItemListView({
    super.key,
  });

  static const routeName = '/list';

  @override
  _SampleItemListViewState createState() => _SampleItemListViewState();
}

class _SampleItemListViewState extends State<SampleItemListView> {
  _SampleItemListViewState();

  List<Sample> items = [];
  bool itemsRequested = false;

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) {
      if (!itemsRequested) {
        // Request items from the server.
        Requests.get('http://localhost:5678/aview/tree', queryParameters: {'order': 'id', 'showarchived': 'false'}).then((response) {
          final document = parse(response.content());
          List<Sample> newItems = [];
          document.getElementsByClassName('nav-entry').forEach((element) {
            int id = int.parse(element.attributes['data-id']??'0');
            if (id > 0) {
              newItems.add(Sample(id, element.attributes['data-name']??''));
            }
          });
          setState(() {
            items = newItems;
          });
        });
        itemsRequested = true;
      }
      return const Center(
        child: CircularProgressIndicator(),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Sample Items'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              // Navigate to the settings page. If the user leaves and returns
              // to the app after it has been killed while running in the
              // background, the navigation stack is restored.
              Navigator.restorablePushNamed(context, SettingsView.routeName);
            },
          ),
        ],
      ),

      // To work with lists that may contain a large number of items, it’s best
      // to use the ListView.builder constructor.
      //
      // In contrast to the default ListView constructor, which requires
      // building all Widgets up front, the ListView.builder constructor lazily
      // builds Widgets as they’re scrolled into view.
      body: ListView.builder(
        // Providing a restorationId allows the ListView to restore the
        // scroll position when a user leaves and returns to the app after it
        // has been killed while running in the background.
        restorationId: 'sampleItemListView',
        itemCount: items.length,
        itemBuilder: (BuildContext context, int index) {
          final item = items[index];

          return ListTile(
            title: Text('${item.name}'),
            leading: const CircleAvatar(
              // Display the Flutter Logo image asset.
              foregroundImage: AssetImage('assets/images/flutter_logo.png'),
            ),
            onTap: () {
              // Navigate to the details page. If the user leaves and returns to
              // the app after it has been killed while running in the
              // background, the navigation stack is restored.
              Navigator.restorablePushNamed(
                context,
                SampleItemDetailsView.routeName,
                arguments: item.id,
              );
            }
          );
        },
      ),
    );
  }
}
