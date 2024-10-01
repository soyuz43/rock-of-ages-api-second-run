from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rockapi.models import Rock, Type
from django.contrib.auth.models import User


class RockView(ViewSet):
    """Rock view set"""


    def create(self, request):
        """Handle POST operations

        Returns:
            Response -- JSON serialized instance
        """

        user = request.user

        # Get the data from the request
        name = request.data.get('name')
        weight = request.data.get('weight')
        type_id = request.data.get('type_id')

        # Validate the data
        if not name or not weight or not type_id:
            return Response({'error': 'Missing required fields.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            weight = float(weight)
        except ValueError:
            return Response({'error': 'Weight must be a number.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            type_instance = Type.objects.get(pk=type_id)
        except Type.DoesNotExist:
            return Response({'error': 'Type not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Create the Rock instance
        rock = Rock.objects.create(
            user=user,
            name=name,
            weight=weight,
            type=type_instance
        )

        # Serialize the new Rock instance
        serializer = RockSerializer(rock)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """
        try:
            rocks = Rock.objects.all()
            serializer = RockSerializer(rocks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single item

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            rock = Rock.objects.get(pk=pk)
            rock.delete()
            return Response(None, status=status.HTTP_204_NO_CONTENT)

        except Rock.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RockTypeSerializer(serializers.ModelSerializer):
    """JSON serializer for Type model"""

    class Meta:
        model = Type
        fields = ('label', )

class RockUserSerializer(serializers.ModelSerializer):
    """JSON serializer for User model"""

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', )

class RockSerializer(serializers.ModelSerializer):
    """JSON serializer for Rock model with expanded foreign keys"""

    type = RockTypeSerializer(many=False)
    user = RockUserSerializer(many=False)

    class Meta:
        model = Rock
        fields = ('id', 'name', 'weight', 'user', 'type', )