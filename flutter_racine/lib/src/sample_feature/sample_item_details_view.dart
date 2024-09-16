import 'package:flutter/material.dart';

import 'package:openapi/api.dart';
// TODO: find a better way to get API token
import '../auth/login_view.dart';

import 'package:requests/requests.dart';
import 'package:html/parser.dart';

/// Displays detailed information about a SampleItem.
class SampleItemDetailsView extends StatefulWidget {
  const SampleItemDetailsView({super.key});

  static const routeName = '/sample_item';

  @override
  _SampleItemDetailsViewState createState() => _SampleItemDetailsViewState();
}

class _SampleItemDetailsViewState extends State<SampleItemDetailsView> {
  String content = '';
  final _samplenameController = TextEditingController();

  int get id => ModalRoute.of(context)!.settings.arguments as int;
  ApiClient? client;

  @override
  Widget build(BuildContext context) {
    if (client == null) {
      final auth = HttpBearerAuth();
      auth.accessToken = apiToken;
      client = ApiClient(basePath: 'http://localhost:5678', authentication: auth);
    }

    if (content == '') {
      Requests.get('http://localhost:5678/aview/editor/$id').then((response) {
        setState(() {
          final document = parse(response.content());
          final samplename = document.getElementById('samplename')?.text;
          _samplenameController.text = samplename ?? '';
          content = response.content();
        });
      });
    }

    _samplenameController.addListener(() {
      print('samplename: ${_samplenameController.text}');
      final api = FieldsApi(client);
      api.setField('sample', id, 'name', value: _samplenameController.text).then((value) => {
        print('setField done')
      });
    });

    return Scaffold(
      appBar: AppBar(
        title: const Text('Item Details'),
      ),
      body: Column(
        children: [
          TextFormField(
                controller: _samplenameController,
                decoration: const InputDecoration(labelText: 'Sample name'),
          ),
          Text(content),
        ]
      ),
    );
  }
}
